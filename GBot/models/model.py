from sqlalchemy import Table, Column, String, MetaData, BigInteger, JSON, Boolean

meta = MetaData()


guild = Table(
    "guild",
    meta,
    Column("id", BigInteger(), nullable=False, primary_key=True),
    Column("prefix", String(8), nullable=False, server_default="g!"),
    Column("auth", Boolean(), nullable=False),
    Column("auth_ch", BigInteger(), nullable=True),
)

VirtualMoney = Table(
    "VirtualMoney",
    meta,
    Column("id", BigInteger(), nullable=False, primary_key=True),
    Column("all_moneys", BigInteger(), nullable=False, server_default="1000"),
    Column("unit", String(3), nullable=False, server_default="JPY"),
    Column("members", JSON(), nullable=False),
)

auth = Table(
    "auth",
    meta,
    Column("user_id", BigInteger(), nullable=False, primary_key=True),
    Column("passcord", String(4))
)
