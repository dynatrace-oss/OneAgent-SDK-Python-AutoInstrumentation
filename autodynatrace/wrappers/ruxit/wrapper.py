import wrapt

from ...log import logger
from ...sdk import sdk


def instrument():
    @wrapt.patch_function_wrapper("ruxit.api.base_plugin", "BasePlugin._query_internal")
    def query_dynatrace(wrapped, instance, args, kwargs):
        plugin_name = type(instance).__name__
        with sdk.trace_custom_service("query", plugin_name):
            logger.debug("Custom tracing - {}: {}".format(plugin_name, "query"))
            return wrapped(*args, **kwargs)
