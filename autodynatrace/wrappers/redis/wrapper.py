import redis
import wrapt
import oneagent
import socket

from ...log import logger
from ...sdk import sdk

from .utils import format_command_args


def instrument():
    if redis.VERSION < (3, 0, 0):
        wrapt.wrap_function_wrapper("redis", "StrictRedis.execute_command", dynatrace_execute_command)
        wrapt.wrap_function_wrapper("redis.client", "BasePipeline.execute", dynatrace_execute_pipeline)
        wrapt.wrap_function_wrapper("redis.client", "BasePipeline.immediate_execute_command", dynatrace_execute_command)
    else:
        wrapt.wrap_function_wrapper("redis", "Redis.execute_command", dynatrace_execute_command)
        wrapt.wrap_function_wrapper("redis.client", "Pipeline.execute", dynatrace_execute_command)
        wrapt.wrap_function_wrapper("redis.client", "Pipeline.immediate_execute_command", dynatrace_execute_command)


def dynatrace_execute_command(func, instance, args, kwargs):
    host = instance.connection_pool.connection_kwargs.get("host", None)
    port = instance.connection_pool.connection_kwargs.get("port", None)

    channel = oneagent.sdk.Channel(oneagent.sdk.ChannelType.OTHER, None)
    if host and port:
        try:
            socket.inet_pton(socket.AF_INET6, host)
            host = "[{}]".format(host)
        except Exception:
            pass
        channel = oneagent.sdk.Channel(oneagent.sdk.ChannelType.TCP_IP, "{}:{}".format(host, port))

    db_info = sdk.create_database_info("Cache", "Redis", channel)

    query = format_command_args(args)
    with sdk.trace_sql_database_request(db_info, query):
        logger.debug("Tracing from Redis: {} {}".format(func.__name__, query))
        return func(*args, **kwargs)


def dynatrace_execute_pipeline(func, instance, args, kwargs):
    cmds = [format_command_args(c) for c, _ in instance.command_stack]
    with sdk.trace_custom_service(func.__name__, "Redis"):
        logger.debug("Tracing from Redis: {} {}".format(func.__name__, cmds))
        sdk.add_custom_request_attribute("Queries", cmds)

        return func(*args, **kwargs)
