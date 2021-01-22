import psycopg2
import wrapt
import oneagent
import functools

from ...log import logger
from ...sdk import sdk


def instrument():
    def parse_dsn(dsn):
        return {c.split("=")[0]: c.split("=")[1] for c in dsn.split() if "=" in c}

    class DynatraceCursor(psycopg2.extensions.cursor):
        def __init__(self, *args, **kwargs):
            self._dynatrace_db_info = kwargs.pop("dynatrace_db_info", None)
            super(DynatraceCursor, self).__init__(*args, **kwargs)

        def execute(self, query, vars=None):
            if hasattr(self, "_dynatrace_db_info") and self._dynatrace_db_info is not None:
                with sdk.trace_sql_database_request(self._dynatrace_db_info, query) as tracer:
                    try:
                        logger.debug("Tracing psycopg2 query: '{}'".format(query))
                        return super(DynatraceCursor, self).execute(query, vars)
                    finally:
                        tracer.set_rows_returned(self.rowcount)

            return super(DynatraceCursor, self).execute(query, vars)

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

            self._dynatrace_cursor = functools.partial(DynatraceCursor, dynatrace_db_info=self._dynatrace_db_info)

        def cursor(self, *args, **kwargs):
            kwargs.setdefault("cursor_factory", self._dynatrace_cursor)
            return super(DynatraceConnection, self).cursor(*args, **kwargs)


    @wrapt.patch_function_wrapper("psycopg2", "connect")
    def dynatrace_connect(wrapped, instance, args, kwargs):
        kwargs.setdefault('connection_factory', DynatraceConnection)
        return wrapped(*args, **kwargs)
