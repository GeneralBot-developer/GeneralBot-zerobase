import os
import asyncio
from aiomysql.sa import create_engine, Engine, SAConnection
from aiomysql.sa.result import ResultProxy


class DataBaseEntryPoint:
    _connection: SAConnection = None

    async def __aenter__(self, loop=None) -> "DataBaseEntryPoint":
        if loop is None:
            loop = asyncio.get_event_loop()
        engine: Engine = await create_engine(
            user=os.environ["MYSQL_USER"],
            db=os.environ["MYSQL_DATABASE"],
            host="mysql",
            port=3306,
            password=os.environ["MYSQL_PASSWORD"],
            charset="utf8",
            autocommit=True,
            loop=loop
        )
        self._connection: SAConnection = await engine.acquire()
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        await self._connection.close()

    async def execute(self, query, *args, **kwargs) -> ResultProxy:
        return await self._connection.execute(query, *args, **kwargs)
