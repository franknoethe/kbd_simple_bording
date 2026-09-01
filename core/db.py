import pymysql
from pymysql import Error
from pymysql.constants import CLIENT

from core.config import DB_CONFIG


class _Connection(pymysql.connections.Connection):
    """Accepts the psycopg2-style cursor_factory kwarg used throughout this file."""

    def cursor(self, cursor=None, cursor_factory=None):
        return super().cursor(cursor_factory or cursor)


def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = _Connection(client_flag=CLIENT.FOUND_ROWS, **DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None
