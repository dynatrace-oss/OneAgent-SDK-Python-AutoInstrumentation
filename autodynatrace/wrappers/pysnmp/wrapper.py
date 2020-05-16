import wrapt

from ...log import logger
from ...sdk import sdk

from pysnmp.proto.rfc1905 import GetRequestPDU, GetBulkRequestPDU


def instrument():
    @wrapt.patch_function_wrapper("pysnmp.proto.rfc3412", "MsgAndPduDispatcher.sendPdu")
    def send_pdu_dynatrace(wrapped, instance, args, kwargs):
        try:
            host, port = args[2]
            request = args[10]

            oids = []
            if isinstance(request, (GetBulkRequestPDU, GetRequestPDU)):
                oids = [str(vb["name"]) for vb in request["variable-bindings"]]

            url = "snmp://{}:{}?query={}".format(host, port, ",".join(oids))

        except Exception as e:
            logger.debug("Could not instrument sendPdu: {}".format(e))
            return wrapped(*args, **kwargs)

        with sdk.trace_outgoing_web_request(url, "POST") as tracer:
            logger.debug("Tracing pysnmp sendPdu, url: '{}'".format(url))
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("pysnmp.proto.rfc3412", "MsgAndPduDispatcher.receiveMessage")
    def send_pdu_dynatrace(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("receiveMessage", "SNMP"):
            logger.debug("Tracing pysnmp receiveMessage")
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("pysnmp.proto.rfc3412", "MsgAndPduDispatcher.returnResponsePdu")
    def send_pdu_dynatrace(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("returnResponsePdu", "SNMP"):
            logger.debug("Tracing pysnmp returnResponsePdu")
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("pysnmp.entity.rfc3413.cmdgen", "CommandGenerator.processResponsePdu")
    def send_pdu_dynatrace(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("processResponsePdu", "SNMP"):
            logger.debug("Tracing pysnmp processResponsePdu")
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("pysnmp.entity.rfc3413.cmdgen", "BulkCommandGeneratorSingleRun.sendVarBinds")
    def send_pdu_dynatrace(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("sendVarBinds", "SNMP"):
            logger.debug("Tracing pysnmp sendVarBinds")
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("pysnmp.hlapi.asyncore.cmdgen", "bulkCmd")
    def send_pdu_dynatrace(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("cmdgen.bulkCmd", "SNMP"):
            logger.debug("Tracing pysnmp cmdgen.bulkCmd")
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("pysnmp.hlapi.asyncore", "bulkCmd")
    def send_pdu_dynatrace(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("asyncore.bulkCmd", "SNMP"):
            logger.debug("Tracing pysnmp asyncore.bulkCmd")
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("pysnmp.hlapi.asyncore", "getCmd")
    def send_pdu_dynatrace(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("asyncore.getCmd", "SNMP"):
            logger.debug("Tracing pysnmp asyncore.getCmd")
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("pysnmp.hlapi", "bulkCmd")
    def send_pdu_dynatrace(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("sync.bulkCmd", "SNMP"):
            logger.debug("Tracing pysnmp sync.bulkCmd")
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("pysnmp.entity.engine", "SnmpEngine.__init__")
    def send_pdu_dynatrace(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("SnmpEngine()", "SNMP"):
            logger.debug("Tracing pysnmp SnmpEngine.__init__")
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("pysnmp.hlapi.lcd", "CommandGeneratorLcdConfigurator.configure")
    def send_pdu_dynatrace(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("configure", "SNMP"):
            logger.debug("Tracing pysnmp CommandGeneratorLcdConfigurator.configure")
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("pysnmp.hlapi.varbinds", "CommandGeneratorVarBinds.makeVarBinds")
    def send_pdu_dynatrace(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("makeVarBinds", "SNMP"):
            logger.debug("Tracing pysnmp CommandGeneratorVarBinds.makeVarBinds")
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("pysnmp.hlapi.asyncore.cmdgen", "getCmd")
    def send_pdu_dynatrace(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("cmdgen.getCmd", "SNMP"):
            logger.debug("Tracing pysnmp cmdgen.getCmd")
            return wrapped(*args, **kwargs)
