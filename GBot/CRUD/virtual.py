from GBot.models import model
from GBot.db import DataBaseEntryPoint as DB


class CRUDBase:
    @staticmethod
    async def execute(query, *args, **kwargs):
        async with DB() as db:
            result = await db.execute(query, *args, **kwargs)
        return result


class VirtualMoney(CRUDBase):
    def __init__(self, guild_id):
        self.guild_id = guild_id

    async def get(self):
        q = model.VirtualMoney.select().where(self.guild_id == model.VirtualMoney.c.id)
        result = await self.execute(q)
        return await result.fetchone()

    async def set(self, **kwargs):
        q = model.VirtualMoney.update(None).where(
            self.guild_id == model.VirtualMoney.c.id
        ).values(**kwargs)
        await self.execute(q)
        return self

    async def delete(self):
        q = model.VirtualMoney.delete(None).where(self.guild_id == model.VirtualMoney.c.id)
        await self.execute(q)
        return self

    @classmethod
    async def create(cls, id, unit):
        q = model.VirtualMoney.insert(None).values(id=id, unit=unit)
        VirtualMoney = cls(id)
        await cls.execute(q)
        return VirtualMoney

    @staticmethod
    async def get_all(cls):
        q = model.VirtualMoney.select()
        results = await cls.execute(q)
        return await results.fetchall()
