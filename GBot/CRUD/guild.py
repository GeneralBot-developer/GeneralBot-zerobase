from GBot.models import guild
from GBot.db import DataBaseEntryPoint


class CRUDBase:
    @staticmethod
    async def execute(query, *args, **kwargs):
        async with DataBaseEntryPoint() as db:
            result = await db.execute(query, *args, **kwargs)
        return result


class Guild(CRUDBase):
    def __init__(self, guild_id):
        self.guild_id = guild_id

    async def get(self):
        q = guild.guild.select().where(self.guild_id == guild.guild.c.id)
        result = await self.execute(q)
        return await result.fetchone()

    async def set(self, **kwargs):
        q = guild.guild.update(None).where(
            self.guild_id == guild.guild.c.id
        ).values(**kwargs)
        await self.execute(q)
        return self

    async def delete(self):
        q = guild.guild.delete(None).where(self.guild_id == guild.guild.c.id)
        await self.execute(q)
        return self

    @classmethod
    async def create(cls, guild_id):
        q = guild.guild.insert(None).values(id=guild_id)
        guild = cls(guild_id)
        await cls.execute(q)
        return guild

    @staticmethod
    async def get_all(cls):
        q = guild.guild.select()
        results = await cls.execute(q)
        return await results.fetchall()
