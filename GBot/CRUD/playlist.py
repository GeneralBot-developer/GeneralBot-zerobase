from GBot.models.model import playlist
from GBot.db import DataBaseEntryPoint as DB


class CRUDBase:

    @staticmethod
    async def execute(query, *args, **kwargs):
        async with DB() as db:
            result = await db.execute(query, *args, **kwargs)
        return result


class PlayList(CRUDBase):

    def __init__(self, playlist_name):
        self.playlist_name = playlist_name

    async def get(self):
        q = playlist.select().where(
            self.playlist_name == playlist.c.playlist_name)
        result = await self.execute(q)
        return await result.fetchone()

    async def set(self, **kwargs):
        q = playlist.update(None).where(
            self.playlist_name == playlist.c.playlist_name).values(**kwargs)
        await self.execute(q)
        return self

    async def delete(self):
        q = playlist.delete(None).where(
            self.playlist_name == playlist.c.playlist_name)
        await self.execute(q)
        return self

    @classmethod
    async def create(cls, **kwargs):
        q = playlist.insert(None).values(**kwargs)
        auth = cls(**kwargs["playlist_name"])
        await cls.execute(q)
        return auth

    @staticmethod
    async def get_all(cls):
        q = playlist.select()
        results = await cls.execute(q)
        return await results.fetchall()
