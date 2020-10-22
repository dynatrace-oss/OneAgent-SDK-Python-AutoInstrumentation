import functools
import os

from ...log import logger
from ...sdk import sdk


def use_fully_qualified_name():
    return os.environ.get("AUTODYNATRACE_CUSTOM_SERVICE_USE_FQN") \
           and os.environ.get("AUTODYNATRACE_CUSTOM_SERVICE_USE_FQN").lower() == 'true'


def get_custom_defined_service_name():
    return os.environ.get("AUTODYNATRACE_CUSTOM_SERVICE_NAME")


def generate_service_name(wrapped):
    if get_custom_defined_service_name():
        return get_custom_defined_service_name()
    else:
        return get_module_path(wrapped)


def get_module_path(wrapped):
    module_path = wrapped.__module__
    class_name = None
    qual_name = None
    result = module_path

    if hasattr(wrapped, "im_class"):
        class_name = wrapped.im_class.__name__
        result = class_name

    if hasattr(wrapped, "__qualname__") and "." in wrapped.__qualname__:
        qual_name = wrapped.__qualname__.split(".")[0]
        result = qual_name

    if use_fully_qualified_name():
        result = ".".join([i for i in [module_path, class_name, qual_name] if i])

    return result


def generate_method_name(wrapped):
    name = wrapped.__name__
    if get_custom_defined_service_name() or use_fully_qualified_name():
        path = get_module_path(wrapped)
        return "{}.{}".format(path, name)
    else:
        return name


def dynatrace_custom_tracer(wrapped):
    @functools.wraps(wrapped)
    def wrapper(*args, **kwargs):
        method_name = generate_method_name(wrapped)
        service_name = generate_service_name(wrapped)

        with sdk.trace_custom_service(method_name, service_name):
            logger.debug("Custom tracing - {}: {}".format(service_name, method_name))
            return wrapped(*args, **kwargs)

    return wrapper
