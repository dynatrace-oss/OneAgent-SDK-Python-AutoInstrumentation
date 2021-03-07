import fastapi
from fastapi.middleware import Middleware
from .middleware import DynatraceASGIMiddleware
import wrapt

from ...log import logger
from ...sdk import sdk


def instrument():
    @wrapt.patch_function_wrapper("fastapi.applications", "FastAPI.__init__")
    def init_dynatrace(wrapped, instance, args, kwargs):
        middlewares = kwargs.pop("middleware", [])
        middlewares.insert(0, Middleware(DynatraceASGIMiddleware))
        kwargs.update({"middleware": middlewares})
        return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("fastapi", "routing.run_endpoint_function")
    async def session_init_dynatrace(wrapped, instance, args, kwargs):
        try:
            name = kwargs.get("dependant").call.__name__
        except Exception:
            name = "run_endpoint_function"

        logger.debug("Tracing fastapi.{}".format(name))
        with sdk.trace_custom_service(name, "FastAPI"):
            return await wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("fastapi", "routing.serialize_response")
    async def serialize_response_dynatrace(wrapped, instance, args, kwargs):
        logger.debug("Tracing fastapi.routing.serialize_response")
        with sdk.trace_custom_service("serialize_response", "FastAPI"):
            return await wrapped(*args, **kwargs)
