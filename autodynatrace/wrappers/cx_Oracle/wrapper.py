import re
import socket

import cx_Oracle
import wrapt

from ...log import logger
from ...sdk import sdk


import oneagent


class DynatraceConnection(cx_Oracle.Connection):
    def __init__(self, *args, **kwargs):
        super(DynatraceConnection, self).__init__(*args, **kwargs)


class DynatraceCursor(cx_Oracle.Cursor):
    def __init__(self, *args, **kwargs):
        super(DynatraceCursor, self).__init__(*args, **kwargs)


def instrument():
    def trace_query(wrapped, instance, args, kwargs):
        if args:
            query = args[0]
            dsn = instance.connection.dsn or "unknown_oracle"
            host = None
            port = 1521

            host_match = re.search(r"HOST=(.*?)\)", dsn)
            if host_match and host_match.groups():
                host = host_match.group(1)

            port_match = re.search(r"PORT=(.*?)\)", dsn)
            if port_match and port_match.groups():
                port = port_match.group(1)

            service_name = dsn
            service_match = re.search(r"SERVICE_NAME=(.*?)\)", dsn)
            if service_match and service_match.groups():
                service_name = service_match.group(1)

            channel = oneagent.sdk.Channel(oneagent.sdk.ChannelType.OTHER, "Oracle")
            if host is not None:
                try:
                    socket.inet_pton(socket.AF_INET6, host)
                    host = "[{}]".format(host)
                except Exception:
                    pass
                channel = oneagent.sdk.Channel(oneagent.sdk.ChannelType.TCP_IP, "{}:{}".format(host, port))

            db_info = sdk.create_database_info(service_name, oneagent.sdk.DatabaseVendor.ORACLE, channel)
            with sdk.trace_sql_database_request(db_info, query):
                logger.debug(
                    "Tracing cx_Oracle query: '{}', host: '{}', port: '{}', database: '{}'".format(
                        query, host, port, service_name
                    )
                )
                return wrapped(*args, **kwargs)

        return wrapped(*args, **kwargs)

    def fetchone_wrapper(wrapped, instance, args, kwargs):
        if not getattr(instance, "_dt_fetchone_reported", False):
            with sdk.trace_custom_service("fetchone", "cx_Oracle"):
                setattr(instance, "_dt_fetchone_reported", True)
                sdk.add_custom_request_attribute("Note", "Only the first fetch (slowest) is recorded")
                return wrapped(*args, **kwargs)
        return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("cx_Oracle", "connect")
    def connect_dynatrace(wrapped, instance, args, kwargs):
        return DynatraceConnection(*args, **kwargs)

    @wrapt.patch_function_wrapper("autodynatrace.wrappers.cx_Oracle.wrapper", "DynatraceConnection.cursor")
    def cursor_dynatrace(wrapped, instance, args, kwargs):
        return DynatraceCursor(instance, *args, **kwargs)

    @wrapt.patch_function_wrapper("autodynatrace.wrappers.cx_Oracle.wrapper", "DynatraceCursor.execute")
    def execute_dynatrace(wrapped, instance, args, kwargs):
        return trace_query(wrapped, instance, args, kwargs)

    @wrapt.patch_function_wrapper("autodynatrace.wrappers.cx_Oracle.wrapper", "DynatraceCursor.executemany")
    def execute_many_dynatrace(wrapped, instance, args, kwargs):
        return trace_query(wrapped, instance, args, kwargs)

    @wrapt.patch_function_wrapper("autodynatrace.wrappers.cx_Oracle.wrapper", "DynatraceCursor.fetchone")
    def fetchone_dynatrace(wrapped, instance, args, kwargs):
        return fetchone_wrapper(wrapped, instance, args, kwargs)

    @wrapt.patch_function_wrapper("autodynatrace.wrappers.cx_Oracle.wrapper", "DynatraceCursor.fetchmany")
    def fetchmany_dynatrace(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("fetchmany", "cx_Oracle"):
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("autodynatrace.wrappers.cx_Oracle.wrapper", "DynatraceCursor.fetchall")
    def fetchall_dynatrace(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("fetchall", "cx_Oracle"):
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("autodynatrace.wrappers.cx_Oracle.wrapper", "DynatraceCursor.__next__")
    def next_dynatrace(wrapped, instance, args, kwargs):
        return fetchone_wrapper(wrapped, instance, args, kwargs)
