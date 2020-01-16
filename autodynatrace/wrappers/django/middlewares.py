import django
from django.conf import settings


from ...log import logger
from ...sdk import sdk
from ..utils import func_name

from .utils import get_request_uri, get_host

try:
    from django.utils.deprecation import MiddlewareMixin

    MiddlewareClass = MiddlewareMixin
except ImportError:
    MiddlewareClass = object


class DynatraceMiddleware(MiddlewareClass):
    def process_request(self, request):
        try:
            url = get_request_uri(request)
            logger.debug("Tracing request {}".format(url))
            host = get_host(request)
            method = request.method

            wappinfo = sdk.create_web_application_info(host, "Django", "/")
            tracer = sdk.trace_incoming_web_request(wappinfo, url, method, headers=request.headers)
            tracer.start()
            _set_req_tracer(request, tracer)

        except Exception:
            logger.debug("Error tracing request")

    def process_view(self, request, view_func, *args, **kwargs):
        name = func_name(view_func)
        logger.debug("Starting view tracer {}".format(name))
        tracer = sdk.trace_custom_service(name, "Django Views")
        tracer.start()
        _add_child_tracer(request, tracer)

    def process_response(self, request, response):
        try:
            tracer = _get_req_tracer(request)
            if tracer:
                tracer.set_status_code(response.status_code)
                tracer.end()

            for child in _get_child_tracers(request):
                if child:
                    child.end()

        except Exception:
            logger.debug("Error processing response", exc_info=True)
        finally:
            return response


def _get_req_tracer(request):
    return getattr(request, "_dynatrace_tracer", None)


def _set_req_tracer(request, tracer):
    return setattr(request, "_dynatrace_tracer", tracer)


def _add_child_tracer(request, tracer):
    tracers = _get_child_tracers(request)
    tracers.append(tracer)
    setattr(request, "_dynatrace_child_tracers", tracers)


def _get_child_tracers(request):
    return getattr(request, "_dynatrace_child_tracers", [])


def get_middleware_insertion_point():
    middleware = getattr(settings, "MIDDLEWARE", None)
    if middleware is not None and django.VERSION >= (1, 10):
        return "MIDDLEWARE", middleware
    return "MIDDLEWARE_CLASSES", getattr(settings, "MIDDLEWARE_CLASSES", None)


def insert_dynatrace_middleware():
    middleware_attribute, middleware = get_middleware_insertion_point()
    if middleware is not None:
        setattr(
            settings,
            middleware_attribute,
            type(middleware)(("autodynatrace.wrappers.django.middlewares.DynatraceMiddleware",)) + middleware,
        )
