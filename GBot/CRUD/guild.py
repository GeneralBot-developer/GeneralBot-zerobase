from GBot.models import model as model
from GBot.db import DataBaseEntryPoint as DB


class CRUDBase:
    @staticmethod
    async def execute(query, *args, **kwargs):
        async with DB() as db:
            result = await db.execute(query, *args, **kwargs)
        return result


class Guild(CRUDBase):
    def __init__(self, guild_id):
        self.guild_id = guild_id

    async def get(self):
        q = model.guild.select().where(self.guild_id == model.auth.c.id)
        result = await self.execute(q)
        return await result.fetchone()

    async def set(self, **kwargs):
        q = model.guild.update(None).where(
            self.guild_id == model.auth.c.id
        ).values(**kwargs)
        await self.execute(q)
        return self

    async def delete(self):
        q = model.auth.delete(None).where(self.user_id == model.auth.c.id)
        await self.execute(q)
        return self

    @classmethod
    async def create(cls, guild_id):
        q = model.guild.insert(None).values(id=guild_id)
        guild = cls(guild_id)
        await cls.execute(q)
        return guild

    @staticmethod
    async def get_all(cls):
        q = model.guild.select()
        results = await cls.execute(q)
        return await results.fetchall()
