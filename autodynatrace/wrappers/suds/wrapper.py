import wrapt

from ...log import logger
from ...sdk import sdk


def instrument():
    @wrapt.patch_function_wrapper("suds.client", "Client.__init__")
    def dynatrace_client(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("CreateClient", "Soap"):
            logger.debug("Tracing suds Client.__init__")
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("suds.client", "SoapClient.invoke")
    def dynatrace_client(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service(instance.method.name, "Soap"):
            logger.debug("Tracing suds Client.{}".format(instance.method.name))
            return wrapped(*args, **kwargs)
