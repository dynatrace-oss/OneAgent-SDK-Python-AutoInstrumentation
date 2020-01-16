import functools


from ...log import logger
from ...sdk import sdk


def dynatrace_custom_tracer(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        function_name = function.__name__
        module_name = function.__module__
        with sdk.trace_custom_service(function_name, module_name):
            logger.debug("Custom tracing - {}: {}".format(module_name, function_name))
            return function(*args, **kwargs)

    return wrapper
