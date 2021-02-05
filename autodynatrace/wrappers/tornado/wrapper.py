import os
import wrapt

from ...log import logger
from ...sdk import sdk


def instrument():
    @wrapt.patch_function_wrapper("tornado.web", "RequestHandler._execute")
    def patch_execute(wrapped, instance, args, kwargs):
        request = instance.request

        virtual_host = os.environ.get("AUTODYNATRACE_VIRTUAL_HOST", request.host)
        app_name = os.environ.get("AUTODYNATRACE_APPLICATION_ID", "Tornado")
        context_root = os.environ.get("AUTODYNATRACE_CONTEXT_ROOT", "/")
        wappinfo = sdk.create_web_application_info(virtual_host, app_name, context_root)

        dt_headers = None
        dt_header = instance.request.headers.get("X-Dynatrace")
        if os.environ.get("AUTODYNATRACE_CAPTURE_HEADERS", False):
            dt_headers = dict(instance.request.headers)

        with wappinfo:
            url = instance.request.full_url().rsplit("?", 1)[0]
            logger.debug("tornado - tracing '{}' with header: '{}'".format(url, dt_header))
            method = instance.request.method
            tracer = sdk.trace_incoming_web_request(wappinfo, url, method, headers=dt_headers, str_tag=dt_header)
            tracer.start()
            sdk.add_custom_request_attribute("query", instance.request.query)

            setattr(instance.request, "__dynatrace_tracer", tracer)
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("tornado.web", "RequestHandler.on_finish")
    def patch_on_finish(wrapped, instance, args, kwargs):
        tracer = getattr(instance.request, "__dynatrace_tracer", None)
        if tracer:
            tracer.set_status_code(instance.get_status())
            tracer.end()

        return wrapped(*args, **kwargs)
