import functools


from ...log import logger
from ...sdk import sdk


def generate_service_name(function):

    service_name = function.__module__
    if hasattr(function, "im_class"):
        service_name = function.im_class.__name__
    if hasattr(function, "__qualname__") and "." in function.__qualname__:
        service_name = function.__qualname__.split(".")[0]

    return service_name


def dynatrace_custom_tracer(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        method_name = function.__name__
        service_name = generate_service_name(function)

        with sdk.trace_custom_service(method_name, service_name):
            logger.debug("Custom tracing - {}: {}".format(service_name, method_name))
            return function(*args, **kwargs)

    return wrapper
