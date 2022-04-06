from GBot.models import model
from GBot.db import DataBaseEntryPoint as DB
from sqlalchemy.orm.attributes import flag_modified
from GBot.models.model import BBS as BBSModel


class CRUDBase:
    @staticmethod
    async def execute(query, *args, **kwargs):
        async with DB() as db:
            result = await db.execute(query, *args, **kwargs)
        return result


class BBS(CRUDBase):
    def __init__(self, bbs_id):
        self.bbs_id = bbs_id

    async def get(self):
        q = model.bbs.select().where(self.bbs_id == model.bbs.c.bbs_id)
        result = await self.execute(q)
        return await result.fetchone()

    async def set(self, **kwargs):
        q = model.bbs.update(None).where(
            self.bbs_id == model.bbs.c.bbs_id).values(**kwargs)
        await self.execute(q)
        q = model.bbs.select().where(self.bbs_id == model.bbs.c.bbs_id)
        flag_modified(q, "using_channels")
        return self

    async def delete(self):
        q = model.bbs.delete(None).where(self.bbs_id == model.bbs.c.bbs_id)
        await self.execute(q)
        return self

    @classmethod
    async def create(cls, **kwargs):
        q = model.bbs.insert(None).values(**kwargs)
        bbs = cls(kwargs["title"])
        await cls.execute(q)
        return bbs

    @staticmethod
    async def get_all(cls):
        q = model.bbs.select()
        results = await cls.execute(q)
        return await results.fetchall()
