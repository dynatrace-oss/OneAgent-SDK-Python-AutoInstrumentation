import oneagent
import wrapt
from django.conf import settings
from django_stomp.services.producer import Publisher
from ...log import logger
from ...sdk import sdk
from .utils import get_messaging_type_by_queue_name

def instrument_publisher():
    def on_send_message(wrapped, instance, args, kwargs):
        try:
            host, port = settings.STOMP_SERVER_HOST, settings.STOMP_SERVER_PORT
            destination = kwargs.get("queue")
            headers = kwargs.get("headers", {})

        except Exception as e:
            logger.warn("autodynatrace - Could not trace Publisher.send: {}".format(e))
            return wrapped(*args, **kwargs)

        messaging_system = sdk.create_messaging_system_info(
            oneagent.common.MessagingVendor.RABBIT_MQ,
            destination,
            get_messaging_type_by_queue_name(destination),
            oneagent.sdk.Channel(oneagent.sdk.ChannelType.TCP_IP, "{}:{}".format(host, port)),
        )

        tag = headers.get(oneagent.common.DYNATRACE_MESSAGE_PROPERTY_NAME, None)
        with messaging_system:
            with sdk.trace_outgoing_message(messaging_system) as outgoing_message:
                outgoing_message.set_correlation_id(headers.get("correlation-id"))
                if not tag:
                    tag = outgoing_message.outgoing_dynatrace_string_tag.decode("utf-8")
                    headers[oneagent.common.DYNATRACE_MESSAGE_PROPERTY_NAME] = tag
                logger.debug(
                    f"autodynatrace - Tracing Outgoing RabbitMQ host={host}, port={port}, routing_key={destination}, "
                    f"tag={tag}, headers={headers}"
                )
                return wrapped(*args, **kwargs)

    wrapt.wrap_function_wrapper(Publisher, "send", on_send_message)
