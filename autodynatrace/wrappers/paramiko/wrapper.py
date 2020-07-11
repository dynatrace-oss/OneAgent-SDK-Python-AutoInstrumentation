import wrapt

from ...log import logger
from ...sdk import sdk


def instrument():
    @wrapt.patch_function_wrapper("paramiko.client", "SSHClient.connect")
    def paramiko_connect(wrapped, instance, args, kwargs):
        host = args[0]
        port = kwargs.get("port", 22)
        url = "ssh://{}:{}".format(host, port)

        with sdk.trace_outgoing_web_request(url, "POST") as tracer:
            logger.debug("Tracing paramiko SSHClient.connect, url: '{}'".format(url))
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("paramiko.client", "SSHClient.exec_command")
    def paramiko_exec_command(wrapped, instance, args, kwargs):
        cmd = args[0]
        with sdk.trace_custom_service("exec_command", "Paramiko"):
            logger.debug("Tracing paramiko SSHClient.exec_command, cmd: '{}'".format(cmd))
            sdk.add_custom_request_attribute("Command", cmd)
            return wrapped(*args, **kwargs)
