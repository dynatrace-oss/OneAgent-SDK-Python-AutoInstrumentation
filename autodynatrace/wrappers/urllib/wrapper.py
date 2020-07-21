import six
import wrapt

from ...log import logger
from ...sdk import sdk


def instrument():
    httplib = six.moves.http_client

    def dynatrace_putrequest(wrapped, instance, args, kwargs):
        method, path = args[:2]
        scheme = "https" if isinstance(instance, httplib.HTTPSConnection) else "http"
        url = "{}://{}{}{}".format(
            scheme, instance.host, ":{}".format(instance.port) if str(instance.port) not in ["80", "443"] else "", path
        )
        tracer = sdk.trace_outgoing_web_request(url, method)
        tracer.start()
        setattr(instance, "__dynatrace_tracer", tracer)
        ret = wrapped(*args, **kwargs)
        tag = tracer.outgoing_dynatrace_string_tag
        logger.debug("Tracing urllib, url: '{}', tag: '{}'".format(url, tag))
        instance.putheader("x-dynatrace", tag)
        return ret

    def dynatrace_getresponse(wrapped, instance, args, kwargs):
        tracer = getattr(instance, "__dynatrace_tracer", None)
        response = wrapped(*args, **kwargs)
        # print(traceback.print_stack())

        if tracer is not None:
            tracer.set_status_code(response.status)
            tracer.end()
            delattr(instance, "__dynatrace_tracer")

        return response

    setattr(httplib.HTTPConnection, "putrequest", wrapt.FunctionWrapper(httplib.HTTPConnection.putrequest, dynatrace_putrequest))
    setattr(
        httplib.HTTPConnection, "getresponse", wrapt.FunctionWrapper(httplib.HTTPConnection.getresponse, dynatrace_getresponse)
    )
