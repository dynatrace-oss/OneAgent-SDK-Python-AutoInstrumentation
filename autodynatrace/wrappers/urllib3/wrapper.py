import urllib3
import wrapt

from ...log import logger
from ...sdk import sdk


def instrument():
    @wrapt.patch_function_wrapper("urllib3", "HTTPConnectionPool.urlopen")
    def urlopen_dynatrace(wrapped, instance, args, kwargs):

        host = instance.host
        port = instance.port
        headers = instance.headers

        if args is not None and len(args) == 2:
            method = args[0]
            path = args[1]
        else:
            method = kwargs.get("method", "GET")
            path = kwargs.get("path", None)
            if path is None:
                path = kwargs.get("url", None)

        protocol = "http" if type(instance) is urllib3.connectionpool.HTTPConnectionPool else "https"
        url = "{}://{}{}{}".format(protocol, host, ":{}".format(port) if str(port) not in ["80", "443"] else "", path)

        with sdk.trace_outgoing_web_request(url, method, headers=headers) as tracer:
            dynatrace_tag = tracer.outgoing_dynatrace_string_tag

            headers = kwargs.get("headers", {})
            headers["x-dynatrace"] = dynatrace_tag
            kwargs["headers"] = headers

            logger.debug('Tracing urllib3. URL: "{}", x-dynatrace: {}'.format(url, dynatrace_tag))
            rv = wrapped(*args, **kwargs)
            try:
                tracer.set_status_code(rv.status)
                tracer.add_response_headers(rv.headers)
            finally:
                return rv
