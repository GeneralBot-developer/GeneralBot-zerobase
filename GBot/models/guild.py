from sqlalchemy import Table, Column, String, MetaData, BigInteger
from sqlalchemy.ext.declarative import declarative_base

meta = MetaData()
Base = declarative_base()


class guild(Base):
    __table__ = Table(
        "guild",
        meta,
        Column("id", BigInteger(), nullable=False, primary_key=True),
        Column("prefix", String(8), nullable=False, server_default="g!"),
        )
