import asyncio
from typing import Coroutine

import wrapt

from ...log import logger
from ...sdk import sdk


def instrument():

    @wrapt.patch_function_wrapper("asyncio.tasks", "ensure_future")
    def dynatrace_coroutine(wrapped, instance, args, kwargs):
        if args and len(args) > 0:
            first_arg = args[0]
            if asyncio.iscoroutine(first_arg):
                args = (trace_coro(first_arg),) + args[1:]

        return wrapped(*args, **kwargs)

    async def trace_coro(coro: Coroutine):
        name = coro.__qualname__
        with sdk.trace_custom_service(name, "asyncio") as tracer:
            try:
                logger.debug(f"tracing asyncio.tasks.ensure_future: {name}")
                return await coro
            finally:
                logger.debug(f"finished asyncio.tasks.ensure_future: {name}")

    @wrapt.patch_function_wrapper("asyncio.base_events", "BaseEventLoop.run_until_complete")
    def dynatrace_run_until_complete(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("run_until_complete", "asyncio"):
            return wrapped(*args, **kwargs)

