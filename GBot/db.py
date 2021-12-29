from sqlalchemy import create_engine
import os
from logging import getLogger

LOG = getLogger(__name__)


class DataBaseEntryPoint:
    def __enter__(self):
        engine = create_engine(
            os.environ["POSTGRESQL_DATABASE_URL"]
        )
        LOG.info("PostgeSQLに接続開始")
        self._connect = engine.connect()
        LOG.info("PostgreSQLに接続完了")
        return self

    def __exit__(self, *args, **kwargs):
        self._connection.close()
        LOG.info("PostgreSQLとの接続を切断")

    def execute(self, query, *args, **kwargs):
        return self._connection.execute(query, *args, **kwargs)
