import aiohttp
import wrapt

from oneagent.common import DYNATRACE_HTTP_HEADER_NAME
from ...log import logger
from ...sdk import sdk


def instrument():
    @wrapt.patch_function_wrapper("aiohttp.client", "ClientSession._request")
    async def dynatrace_request(wrapped, instance, args, kwargs):

        method = args[0]
        url = str(args[1])
        headers = dict(kwargs.get("headers", {}))

        with sdk.trace_outgoing_web_request(url, method, headers) as tracer:
            tag = tracer.outgoing_dynatrace_string_tag.decode()
            logger.debug("dynatrace - tracing {} '{}' with tag '{}'".format(method, url, tag))
            headers.update({DYNATRACE_HTTP_HEADER_NAME: tag})
            kwargs["headers"] = headers

            response = await wrapped(*args, **kwargs)

            tracer.set_status_code(response.status)
            tracer.add_response_headers(dict(response.headers))

            return response
