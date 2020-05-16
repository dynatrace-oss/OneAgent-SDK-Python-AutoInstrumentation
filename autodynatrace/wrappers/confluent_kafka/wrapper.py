import wrapt

from ...log import logger
from ...sdk import sdk
from oneagent.common import MessagingDestinationType
from oneagent.sdk import Channel, ChannelType

import confluent_kafka


class Producer(confluent_kafka.Producer):
    pass


class Consumer(confluent_kafka.Consumer):
    pass


def instrument():
    confluent_kafka.Consumer = Consumer
    confluent_kafka.Producer = Producer

    @wrapt.patch_function_wrapper("autodynatrace.wrappers.confluent_kafka.wrapper", "Producer.__init__")
    def custom_producer_init(wrapped, instance, args, kwargs):

        servers = args[0].get("bootstrap.servers", "unknown-host")
        setattr(instance, "dt_servers", servers)

        return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("autodynatrace.wrappers.confluent_kafka.wrapper", "Consumer.__init__")
    def custom_consumer_init(wrapped, instance, args, kwargs):

        servers = args[0].get("bootstrap.servers", "unknown-host")
        setattr(instance, "dt_servers", servers)

        return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("autodynatrace.wrappers.confluent_kafka.wrapper", "Producer.produce")
    def custom_produce(wrapped, instance, args, kwargs):

        servers = getattr(instance, "dt_servers", "unknown-host")

        msi_handle = sdk.create_messaging_system_info(
            "Kafka", args[0], MessagingDestinationType.TOPIC, Channel(ChannelType.TCP_IP, servers),
        )

        with msi_handle:
            with sdk.trace_outgoing_message(msi_handle) as tracer:
                tag = tracer.outgoing_dynatrace_string_tag
                logger.debug("kafka-producer Injecting message with header '{}'".format(tag))
                headers = kwargs.get("headers", {})
                headers.update({"x-dynatrace": tag})
                kwargs["headers"] = headers
                return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("autodynatrace.wrappers.confluent_kafka.wrapper", "Consumer.poll")
    def custom_poll(wrapped, instance, args, kwargs):
        message = wrapped(*args, **kwargs)
        if message is not None:
            try:
                servers = getattr(instance, "dt_servers", "unknown-host")
                msi_handle = sdk.create_messaging_system_info(
                    "Kafka", message.topic(), MessagingDestinationType.TOPIC, Channel(ChannelType.TCP_IP, servers),
                )
                with msi_handle:
                    tag = None
                    headers = message.headers()
                    if headers is not None:
                        for header in headers:
                            if header[0].lower() == "x-dynatrace":
                                tag = header[1]
                    with sdk.trace_incoming_message_process(msi_handle, str_tag=tag):
                        logger.debug("kafka-consumer: Received message with tag {}".format(tag))
                        return message
            except Exception:
                logger.debug("Could not trace Consumer.poll", exc_info=True)
                return message
        return message
