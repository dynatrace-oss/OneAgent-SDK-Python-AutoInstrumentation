from django.db import connections

from ...log import logger
from ...sdk import sdk
from ..utils import normalize_vendor
from ..dbapi import TracedCursor

import oneagent

import socket

CURSOR_ATTR = "_dynatrace_cursor"
ALL_CONNS_ATTR = "_dynatrace_connections_all"


def instrument_db():
    if hasattr(connections, ALL_CONNS_ATTR):
        return

    setattr(connections, ALL_CONNS_ATTR, connections.all)

    def all_connections(self):
        conns = getattr(self, ALL_CONNS_ATTR)()
        for conn in conns:
            instrument_conn(conn)
        return conns

    connections.all = all_connections.__get__(connections, type(connections))


def instrument_conn(conn):
    if hasattr(conn, CURSOR_ATTR):
        return

    setattr(conn, CURSOR_ATTR, conn.cursor)

    def cursor():
        alias = getattr(conn, "alias", "default")
        vendor = normalize_vendor(getattr(conn, "vendor", "db"))
        logger.debug("Instrumenting the DB {} {}".format(alias, vendor))

        db_technology = conn.settings_dict.get("ENGINE", "SQL").split(".")[-1]
        db_name = conn.settings_dict.get("NAME", "Unknow")
        db_host = conn.settings_dict.get("HOST", None)
        db_port = conn.settings_dict.get("PORT", None)

        channel = oneagent.sdk.Channel(oneagent.sdk.ChannelType.OTHER, None)
        if db_host and db_port:
            try:
                socket.inet_pton(socket.AF_INET6, db_host)
                db_host = "[{}]".format(db_host)
            except Exception:
                pass
            channel = oneagent.sdk.Channel(oneagent.sdk.ChannelType.TCP_IP, "{}:{}".format(db_host, db_port))

        db_info = sdk.create_database_info(db_name, db_technology, channel)
        return TracedCursor(conn._dynatrace_cursor(), db_info)

    conn.cursor = cursor
