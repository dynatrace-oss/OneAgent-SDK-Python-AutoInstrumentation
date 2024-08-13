import socket

import oneagent
import oracledb
import wrapt

from ...log import logger
from ...sdk import sdk


class DynatraceConnection(oracledb.Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DynatraceCursor(oracledb.Cursor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def instrument():
    def trace_query(wrapped, instance, args, kwargs):
        if args:
            query = args[0]
            dsn = instance.connection.dsn

            connect_params = oracledb.ConnectParams()
            connect_params.parse_connect_string(dsn)
            if isinstance(connect_params.host, list):
                host = connect_params.host[0]
                port = connect_params.port[0]
                service_name = connect_params.service_name[0]
            else:
                host = connect_params.host
                port = connect_params.port
                service_name = connect_params.service_name

            channel = oneagent.sdk.Channel(oneagent.sdk.ChannelType.OTHER, "Oracle")
            if host is not None:
                try:
                    socket.inet_pton(socket.AF_INET6, host)
                    host = f"[{host}]"
                except Exception:
                    pass
                channel = oneagent.sdk.Channel(
                    oneagent.sdk.ChannelType.TCP_IP,
                    f"{host}:{port}",
                )

            db_info = sdk.create_database_info(
                service_name,
                oneagent.sdk.DatabaseVendor.ORACLE,
                channel,
            )
            with sdk.trace_sql_database_request(db_info, f"{query}"):
                logger.debug(
                    f"Tracing oracledb query: '{query}', "
                    f"host: '{host}', port: '{port}', database: '{service_name}'",
                )
                return wrapped(*args, **kwargs)

        return wrapped(*args, **kwargs)

    def fetchone_wrapper(wrapped, instance, args, kwargs):
        if not getattr(instance, "_dt_fetchone_reported", False):
            with sdk.trace_custom_service("fetchone", "oracledb"):
                instance._dt_fetchone_reported = True
                sdk.add_custom_request_attribute(
                    "Note",
                    "Only the first fetch (slowest) is recorded",
                )
                return wrapped(*args, **kwargs)
        return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("oracledb", "connect")
    def connect_dynatrace(wrapped, instance, args, kwargs):
        return DynatraceConnection(*args, **kwargs)

    @wrapt.patch_function_wrapper(
        "autodynatrace.wrappers.oracledb.wrapper",
        "DynatraceConnection.cursor",
    )
    def cursor_dynatrace(wrapped, instance, args, kwargs):
        return DynatraceCursor(instance, *args, **kwargs)

    @wrapt.patch_function_wrapper(
        "autodynatrace.wrappers.oracledb.wrapper",
        "DynatraceCursor.execute",
    )
    def execute_dynatrace(wrapped, instance, args, kwargs):
        return trace_query(wrapped, instance, args, kwargs)

    @wrapt.patch_function_wrapper(
        "autodynatrace.wrappers.oracledb.wrapper",
        "DynatraceCursor.executemany",
    )
    def execute_many_dynatrace(wrapped, instance, args, kwargs):
        return trace_query(wrapped, instance, args, kwargs)

    @wrapt.patch_function_wrapper(
        "autodynatrace.wrappers.oracledb.wrapper",
        "DynatraceCursor.fetchone",
    )
    def fetchone_dynatrace(wrapped, instance, args, kwargs):
        return fetchone_wrapper(wrapped, instance, args, kwargs)

    @wrapt.patch_function_wrapper(
        "autodynatrace.wrappers.oracledb.wrapper",
        "DynatraceCursor.fetchmany",
    )
    def fetchmany_dynatrace(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("fetchmany", "oracledb"):
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper(
        "autodynatrace.wrappers.oracledb.wrapper",
        "DynatraceCursor.fetchall",
    )
    def fetchall_dynatrace(wrapped, instance, args, kwargs):
        with sdk.trace_custom_service("fetchall", "oracledb"):
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper(
        "autodynatrace.wrappers.oracledb.wrapper",
        "DynatraceCursor.__next__",
    )
    def next_dynatrace(wrapped, instance, args, kwargs):
        return fetchone_wrapper(wrapped, instance, args, kwargs)
