from GBot.models import model as model
from GBot.db import DataBaseEntryPoint as DB
from aiomysql.sa.result import RowProxy
from collections.abc import Mapping


class CRUDBase:
    @staticmethod
    async def execute(query, *args, **kwargs):
        async with DB() as db:
            result = await db.execute(query, *args, **kwargs)
        return result


class Guild(CRUDBase):
    def __init__(self, guild_id):
        self.guild_id = guild_id

    async def get(self) -> RowProxy:
        q = model.guild.select().where(self.guild_id == model.guild.c.id)
        result = await self.execute(q)
        return await result.fetchone()

    async def set(self, **kwargs):
        q = model.guild.update(None).where(
            self.guild_id == model.guild.c.id
        ).values(**kwargs)
        await self.execute(q)
        return self

    async def delete(self):
        q = model.guild.delete(None).where(self.guild_id == model.guild.c.id)
        await self.execute(q)
        return self

    @classmethod
    async def create(cls, **kwargs):
        q = model.guild.insert(None).values(**kwargs)
        guild = cls(kwargs["id"])
        await cls.execute(q)
        return guild

    @staticmethod
    async def get_all(cls):
        q = model.guild.select()
        results = await cls.execute(q)
        return await results.fetchall()
