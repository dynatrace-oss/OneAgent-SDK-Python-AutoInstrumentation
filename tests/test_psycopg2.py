import autodynatrace

import psycopg2
from psycopg2.extras import RealDictCursor


def test_instrumentation():
    conn = psycopg2.connect("dbname=invictus user=invictus password=password")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT tablename, tableowner FROM pg_catalog.pg_tables")
    for row in cur:
        print(row['tablename'])