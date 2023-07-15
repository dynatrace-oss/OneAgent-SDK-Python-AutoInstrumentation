import oneagent
from django.conf import settings
from django.utils.module_loading import import_string
from django_stomp import execution
from ...log import logger
from ...sdk import sdk
from .utils import get_messaging_type_by_queue_name

def instrument_consumer():
    def wrapped_import_string(dotted_path):
        callback_function = import_string(dotted_path)

        def instrumented_callback(payload):
            try:
                headers = payload.headers
                host, port = settings.STOMP_SERVER_HOST, settings.STOMP_SERVER_PORT
                destination = headers.get("tshoot-destination")
            except Exception as e:
                logger.warn("autodynatrace - Could not trace Consumer(import_string): {}".format(e))
                return callback_function(payload)

            tag = None
            if headers is not None:
                tag = headers.get(oneagent.common.DYNATRACE_MESSAGE_PROPERTY_NAME, None)

            messaging_system = sdk.create_messaging_system_info(
                oneagent.common.MessagingVendor.RABBIT_MQ,
                destination,
                get_messaging_type_by_queue_name(destination),
                oneagent.sdk.Channel(oneagent.sdk.ChannelType.TCP_IP, "{}:{}".format(host, port)),
            )

            with messaging_system:
                with sdk.trace_incoming_message_receive(messaging_system):
                    with sdk.trace_incoming_message_process(messaging_system, str_tag=tag) as process_message:
                        process_message.set_correlation_id(headers.get("correlation-id"))
                        process_message.set_vendor_message_id(headers.get("message-id"))
                        logger.debug(
                            f"autodynatrace - Tracing Incoming RabbitMQ host={host}, port={port},"
                            f" routing_key={destination}, tag={tag}, headers={headers}"
                        )
                        return callback_function(payload)

        return instrumented_callback

    setattr(execution, "import_string", wrapped_import_string)
