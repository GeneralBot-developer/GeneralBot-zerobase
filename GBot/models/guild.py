from sqlalchemy import Table, Column, String, MetaData, BigInteger

meta = MetaData()


guild = Table(
    "guild",
    meta,
    Column("id", BigInteger(), nullable=False, primary_key=True),
    Column("prefix", String(8), nullable=False, server_default="g!"),
)
