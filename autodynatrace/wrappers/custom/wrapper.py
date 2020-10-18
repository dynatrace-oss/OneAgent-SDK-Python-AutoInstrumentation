import functools
import os

from ...log import logger
from ...sdk import sdk


def generate_service_name(wrapped):
    if os.environ.get("AUTODYNATRACE_CUSTOM_SERVICE_NAME"):
        return os.environ.get("AUTODYNATRACE_CUSTOM_SERVICE_NAME")

    service_name = wrapped.__module__
    if hasattr(wrapped, "im_class"):
        service_name = wrapped.im_class.__name__
    if hasattr(wrapped, "__qualname__") and "." in wrapped.__qualname__:
        service_name = wrapped.__qualname__.split(".")[0]

    return service_name


def dynatrace_custom_tracer(wrapped):
    @functools.wraps(wrapped)
    def wrapper(*args, **kwargs):
        method_name = wrapped.__name__
        service_name = generate_service_name(wrapped)

        with sdk.trace_custom_service(method_name, service_name):
            logger.debug("Custom tracing - {}: {}".format(service_name, method_name))
            return wrapped(*args, **kwargs)

    return wrapper
