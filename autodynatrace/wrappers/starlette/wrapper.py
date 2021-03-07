import starlette
import asyncio

import wrapt
from ...log import logger
from ...sdk import sdk


def instrument():
    @wrapt.patch_function_wrapper("starlette.responses", "Response.__init__")
    def starlette_parsing_dynatrace(wrapped, instance, args, kwargs):

        # FastAPI creates a empty response at the beginning of a request, ignore it
        if kwargs.get("status_code") is None:
            return wrapped(*args, **kwargs)

        logger.debug("Tracing starlette.Response.__init__")
        with sdk.trace_custom_service("Response.render", "starlette"):
            return wrapped(*args, **kwargs)

    # TODO - Add asyncio support
    # @wrapt.patch_function_wrapper("asyncio", "BaseEventLoop.create_task")
    # def starlette_parsing_dynatrace(wrapped, instance, args, kwargs):
    #     logger.debug("Tracing asyncio.BaseEventLoop.create_task")
    #     with sdk.trace_custom_service("BaseEventLoop.create_task", "asyncio"):
    #         return wrapped(*args, **kwargs)

    # loop = asyncio.get_event_loop()
    # if not isinstance(loop.create_task, wrapt.ObjectProxy):
    #
    #     @wrapt.patch_function_wrapper(loop, "create_task")
    #     def starlette_parsing_dynatrace(wrapped, instance, args, kwargs):
    #         logger.debug("Tracing asyncio.loop.create_task")
    #         with sdk.trace_custom_service("loop.create_task", "asyncio"):
    #             return wrapped(*args, **kwargs)
