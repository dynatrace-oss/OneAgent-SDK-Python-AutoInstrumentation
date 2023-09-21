from abc import ABC

import psycopg2
import wrapt
import oneagent

from ...log import logger
from ...sdk import sdk


def instrument():
    def parse_dsn(dsn):
        return {c.split("=")[0]: c.split("=")[1] for c in dsn.split() if "=" in c}

    class DynatraceCursor(wrapt.ObjectProxy, ABC):

        def __init__(self, wrapped, dynatrace_db_info):
            super(DynatraceCursor, self).__init__(wrapped)
            self._self_dynatrace_db_info = dynatrace_db_info

        def execute(self, query, vars=None):
            if hasattr(self, "dynatrace_db_info") and self._self_dynatrace_db_info is not None:
                with sdk.trace_sql_database_request(self._self_dynatrace_db_info, "{}".format(query)) as tracer:
                    try:
                        logger.debug("Tracing psycopg2 query: '{}'".format(query))
                        return self.__wrapped__.execute(query, vars)
                    finally:
                        tracer.set_rows_returned(self.__wrapped__.rowcount)

            return self.__wrapped__.execute(query, vars)

    class DynatraceConnection(psycopg2.extensions.connection):
        def __init__(self, *args, **kwargs):
            super(DynatraceConnection, self).__init__(*args, **kwargs)

            dsn = parse_dsn(self.dsn)
            self._dynatrace_db_info = sdk.create_database_info(
                dsn.get("dbname", "unknown"),
                oneagent.sdk.DatabaseVendor.POSTGRESQL,
                oneagent.sdk.Channel(
                    oneagent.sdk.ChannelType.TCP_IP, "{}:{}".format(dsn.get("host", "localhost"), dsn.get("port", 5432))
                ),
            )

        def cursor(self, *args, **kwargs):
            return DynatraceCursor(super(DynatraceConnection, self).cursor(*args, **kwargs), self._dynatrace_db_info)

    @wrapt.patch_function_wrapper("psycopg2", "connect")
    def dynatrace_connect(wrapped, instance, args, kwargs):
        kwargs.setdefault("connection_factory", DynatraceConnection)
        return wrapped(*args, **kwargs)
