import wrapt

from ...log import logger
from ...sdk import sdk
from ..utils import normalize_vendor


class TracedCursor(wrapt.ObjectProxy):
    def __init__(self, cursor, db_info):
        super(TracedCursor, self).__init__(cursor)
        self.db_info = db_info
        self._self_last_execute_operation = None

    def _trace_method(self, method, query, *args, **kwargs):

        logger.debug("Tracing Database Call '{}' to {}".format(query, self.db_info))
        with sdk.trace_sql_database_request(self.db_info, query):
            return method(*args, **kwargs)

    def executemany(self, query, *args, **kwargs):
        self._self_last_execute_operation = query
        return self._trace_method(self.__wrapped__.executemany, query, query, *args, **kwargs)

    def execute(self, query, *args, **kwargs):
        self._self_last_execute_operation = query
        return self._trace_method(self.__wrapped__.execute, query, query, *args, **kwargs)

    def callproc(self, proc, args):
        self._self_last_execute_operation = proc
        return self._trace_method(self.__wrapped__.callproc, proc, proc, args)

    def __enter__(self):
        self.__wrapped__.__enter__()
        return self


class TracedConnection(wrapt.ObjectProxy):
    def __init__(self, conn, cursor_cls=None):

        if not cursor_cls:
            cursor_cls = TracedCursor
        super(TracedConnection, self).__init__(conn)
        self._self_cursor_cls = cursor_cls

    def _trace_method(self, method, *args, **kwargs):
        logger.info("Tracing Connection {}".format(args))
        return method(*args, **kwargs)

    def cursor(self, *args, **kwargs):
        return self.__wrapped__.cursor(*args, **kwargs)

    def commit(self, *args, **kwargs):
        span_name = "commit"
        return self._trace_method(self.__wrapped__.commit, span_name, {}, *args, **kwargs)

    def rollback(self, *args, **kwargs):
        span_name = "rollback"
        return self._trace_method(self.__wrapped__.rollback, span_name, {}, *args, **kwargs)


def _get_vendor(conn):
    try:
        name = _get_module_name(conn)
    except Exception:
        logger.debug("couldnt parse module name", exc_info=True)
        name = "sql"
    return normalize_vendor(name)


def _get_module_name(conn):
    return conn.__class__.__module__.split(".")[0]
