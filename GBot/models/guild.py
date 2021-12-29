from GBot.models import model
from GBot.db import DataBaseEntryPoint


class CRUDBase:
    @staticmethod
    def execute(query, *args, **kwargs):
        with DataBaseEntryPoint() as db:
            result = db.execute(query, *args, **kwargs)
        return result


class Guild(CRUDBase):
    def __init__(self, guild_id):
        self.guild_id = guild_id

    def get(self):
        q = model.guild.select().where(self.guild_id == model.guild.c.id)
        result = self.execute(q)
        return result.fetchone()

    async def set(self, **kwargs):
        q = model.guild.update(None).where(
            self.guild_id == model.guild.c.id
        ).values(**kwargs)
        self.execute(q)
        return self

    def delete(self):
        q = model.guild.delete(None).where(self.guild_id == model.guild.c.id)
        self.execute(q)
        return self

    @classmethod
    def create(cls, guild_id):
        q = model.guild.insert(None).values(id=guild_id)
        guild = cls(guild_id)
        cls.execute(q)
        return guild

    @staticmethod
    def get_all(cls):
        q = model.guild.select()
        results = cls.execute(q)
        return results.fetchall()
