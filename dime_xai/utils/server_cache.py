import logging
import sqlite3
from typing import NoReturn, Text, List

from dime_xai.shared.constants import (
    SERVER_CACHE,
    SERVER_CACHE_TABLE
)
from dime_xai.shared.exceptions.dime_server_exceptions import (
    ServerCacheException,
    ServerCachePushException,
    ServerCachePullException,
)

logger = logging.getLogger(__name__)


def create_in_memory_server_cache() -> NoReturn:
    try:
        with sqlite3.connect(SERVER_CACHE) as conn:
            conn.execute(f'DROP TABLE IF EXISTS {SERVER_CACHE_TABLE};')
            conn.execute(f'CREATE TABLE {SERVER_CACHE_TABLE} '
                         f'(data_instance_id INT PRIMARY KEY, data_instance TEXT NOT NULL);')
            conn.commit()
            logger.debug('In-memory server cache was initialized')
    except Exception as e:
        raise ServerCacheException(e)


class ServerCache:
    def __init__(self):
        self.server_cache = SERVER_CACHE

    def in_memory_server_cache(self) -> Text:
        return self.server_cache

    def push(
            self,
            data_instance_id: int,
            data_instance: Text,
    ) -> bool:
        try:
            with sqlite3.connect(self.server_cache) as conn:
                conn.row_factory = sqlite3.Row
                conn.execute(
                    f'INSERT INTO {SERVER_CACHE_TABLE} VALUES (?, ?)',
                    (data_instance_id, data_instance)
                )
                conn.commit()
            return True
        except Exception as e:
            raise ServerCachePushException(e)

    def remove(
            self,
            data_instance_id: int
    ) -> bool:
        try:
            with sqlite3.connect(self.server_cache) as conn:
                conn.row_factory = sqlite3.Row
                conn.execute(
                    f"DELETE FROM {SERVER_CACHE_TABLE} WHERE data_instance_id = ?",
                    (data_instance_id,)
                )
                conn.commit()
            return True
        except Exception as e:
            raise ServerCacheException(e)

    def check_existence(
            self,
            data_instance_id: int
    ) -> bool:
        try:
            with sqlite3.connect(self.server_cache) as conn:
                conn.row_factory = sqlite3.Row
                data_instance = conn.execute(
                    f"SELECT data_instance FROM {SERVER_CACHE_TABLE} WHERE data_instance_id = ?",
                    (data_instance_id,)
                ).fetchone()
                conn.commit()

            if data_instance:
                return True
            else:
                return False
        except Exception as e:
            raise ServerCacheException(e)

    def purge(
            self,
    ) -> bool:
        try:
            with sqlite3.connect(self.server_cache) as conn:
                conn.row_factory = sqlite3.Row
                conn.execute(
                    f"DELETE FROM {SERVER_CACHE_TABLE}"
                )
                conn.commit()
                return True
        except Exception as e:
            raise ServerCacheException(e)

    def inspect(
            self,
    ) -> List:
        try:
            with sqlite3.connect(self.server_cache) as conn:
                conn.row_factory = sqlite3.Row
                current_server_cache = conn.execute(
                    f"SELECT data_instance FROM {SERVER_CACHE_TABLE}"
                ).fetchall()
                conn.commit()
            return current_server_cache
        except Exception as e:
            raise ServerCachePullException(e)
