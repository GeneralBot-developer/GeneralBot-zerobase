import os
import asyncio
from aiomysql.sa import create_engine


class DataBaseEntryPoint:
    async def __aenter__(self, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        engine = await create_engine(
            user=os.environ["MYSQL_USER"],
            db=os.environ["MYSQL_DATABASE"],
            host="remotemysql.com",
            port=3306,
            password=os.environ["MYSQL_PASSWORD"],
            charset="utf8",
            autocommit=True,
            loop=loop
        )
        self._connection = await engine.acquire()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._connection.close()

    async def execute(self, query, *args, **kwargs):
        return await self._connection.execute(query, *args, **kwargs)
