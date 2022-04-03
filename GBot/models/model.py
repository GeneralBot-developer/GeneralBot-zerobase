from sqlalchemy import Table, Column, String, MetaData, BigInteger, JSON, Boolean, Integer, DateTime

meta = MetaData()


guild = Table(
    "guild",
    meta,
    Column("id", BigInteger(), nullable=False, primary_key=True),
    Column("prefix", String(8), nullable=False, server_default="g!"),
    Column("auth", Boolean(), nullable=False),
    Column("auth_ch", BigInteger(), nullable=True),
    Column("auth_role", BigInteger(), nullable=True),
    Column("automoderation", Boolean(), nullable=False),
    Column("ignore_channels", JSON(), nullable=True),
    Column("ignore_roles", JSON(), nullable=True),
    Column("ignore_users", JSON(), nullable=True),
    Column("message_delete_limit", Integer(), nullable=False, server_default="5"),
)

VirtualMoney = Table(
    "VirtualMoney",
    meta,
    Column("id", BigInteger(), nullable=False, primary_key=True),
    Column("all_moneys", BigInteger(), nullable=False, server_default="1000"),
    Column("unit", String(3), nullable=False, server_default="JPY"),
    Column("members", JSON(), nullable=True),
    Column("stores", JSON(), nullable=True),
)

auth = Table(
    "auth",
    meta,
    Column("user_id", BigInteger(), nullable=False, primary_key=True),
    Column("passcord", String(4), nullable=True)
)

bbs = Table(
    "bbs",
    meta,
    Column("title", String(255), nullable=False),
    Column("author", BigInteger(), nullable=False, primary_key=True),
    Column("content", String(1024), nullable=False),
    Column("created_at", DateTime(), nullable=False),
    Column("updated_at", DateTime(), nullable=True),
    Column("using_channels", JSON(), nullable=True),
)

playlist = Table(
    "playlist",
    meta,
    Column("playlist_name", String(255), nullable=False, primary_key=True),
    Column("author", BigInteger(), nullable=False),
    Column("musics", JSON(), nullable=True)
)
