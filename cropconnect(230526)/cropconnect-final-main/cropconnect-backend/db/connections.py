import threading
import time
from contextlib import contextmanager
from typing import Any

import mysql.connector
from mysql.connector import pooling

_db_config: dict[str, Any] = {}
_mysql_pool_size = 15
_main_db_pool = None
_main_db_pool_lock = threading.Lock()


def configure_connections(db_config: dict[str, Any], mysql_pool_size: int) -> None:
    global _db_config, _mysql_pool_size
    _db_config = {
        "connection_timeout": 10,
        **dict(db_config),
    }
    _mysql_pool_size = max(1, int(mysql_pool_size))


def _get_pooled_connection(pool: pooling.MySQLConnectionPool):
    last_error = None
    for _attempt in range(4):
        try:
            return pool.get_connection()
        except mysql.connector.errors.PoolError as exc:
            last_error = exc
            time.sleep(0.15)
    raise last_error


@contextmanager
def get_connection():
    global _main_db_pool
    if _main_db_pool is None:
        with _main_db_pool_lock:
            if _main_db_pool is None:
                _main_db_pool = pooling.MySQLConnectionPool(
                    pool_name="cropconnect_main",
                    pool_size=_mysql_pool_size,
                    pool_reset_session=True,
                    **_db_config,
                )
    conn = _get_pooled_connection(_main_db_pool)
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_server_connection():
    config = {**_db_config}
    config.pop("database", None)
    conn = mysql.connector.connect(**config)
    try:
        yield conn
    finally:
        conn.close()
