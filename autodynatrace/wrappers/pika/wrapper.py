import pika
import wrapt

from ...log import logger
from ...sdk import sdk

import oneagent


def instrument():
    @wrapt.patch_function_wrapper("pika.channel", "Channel.basic_publish")
    def basic_publish_dynatrace(wrapped, instance, args, kwargs):

        try:
            host = instance.connection.params.host
            port = instance.connection.params.port
            exchange = kwargs.get("exchange")
            routing_key = kwargs.get("routing_key")

        except Exception as e:
            logger.warn("autodynatrace - could not instrument Channel.basic_publish: {}".format(e))
            return wrapped(*args, **kwargs)

        properties = kwargs.get("properties")
        if properties is not None:
            if properties.headers is None:
                properties.headers = {}
        else:
            props = pika.BasicProperties(headers={})
            kwargs["properties"] = props

        messaging_system = sdk.create_messaging_system_info(
            "RabbitMQ",
            routing_key,
            oneagent.common.MessagingDestinationType.QUEUE,
            oneagent.sdk.Channel(oneagent.sdk.ChannelType.TCP_IP, "{}:{}".format(host, port)),
        )
        with messaging_system:
            with sdk.trace_outgoing_message(messaging_system) as tracer:
                tag = tracer.outgoing_dynatrace_string_tag.decode("utf-8")
                kwargs["properties"].headers[oneagent.common.DYNATRACE_MESSAGE_PROPERTY_NAME] = tag
                logger.debug(
                    "autodynatrace - Tracing RabbitMQ host={}, port={}, routing_key={}, tag={}".format(
                        host, port, routing_key, tag
                    )
                )
                return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("pika.adapters.blocking_connection", "BlockingChannel._on_consumer_message_delivery")
    def on_message_callback_dynatrace(wrapped, instance, args, kwargs):

        try:
            channel, method_frame, header_frame, body = args
            host = channel.connection.params.host
            port = channel.connection.params.port
            routing_key = method_frame.routing_key
            exchange = method_frame.exchange
            tag = None
            if header_frame is not None and header_frame.headers is not None:
                tag = header_frame.headers.get(oneagent.common.DYNATRACE_MESSAGE_PROPERTY_NAME, None)

        except Exception as e:
            logger.warn("autodynatrace - Could not trace BlockingChannel._on_consumer_message_delivery: {}".format(e))
            return wrapped(*args, **kwargs)

        messaging_system = sdk.create_messaging_system_info(
            "RabbitMQ",
            routing_key,
            oneagent.common.MessagingDestinationType.QUEUE,
            oneagent.sdk.Channel(oneagent.sdk.ChannelType.TCP_IP, "{}:{}".format(host, port)),
        )
        with messaging_system:
            with sdk.trace_incoming_message_receive(messaging_system):
                logger.debug(
                    "autodynatrace - Tracing RabbitMQ host={}, port={}, routing_key={}, tag={}".format(
                        host, port, routing_key, tag
                    )
                )
                with sdk.trace_incoming_message_process(messaging_system, str_tag=tag):
                    return wrapped(*args, **kwargs)
