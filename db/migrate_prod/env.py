import importlib
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, MetaData
from sqlalchemy import pool

from alembic import context

config = context.config

fileConfig(config.config_file_name)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_ROOT = BASE_DIR + '/../GBot/models/model'
sys.path.append(MODELS_ROOT)

target_models = [
    "guild",
]


class BaseEnv:
    @staticmethod
    def make_target_metadata():
        lst = list(
            map(
                lambda x: importlib.import_module(
                    x
                    ).Base.metadata, target_models
                )
            )
        m = MetaData()
        for metadata in lst:
            for t in metadata.tables.values():
                t.tometadata(m)
        return m


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    config.set_section_option("alembic", "DB_USER", os.environ.get("DB_USER"))
    config.set_section_option(
        "alembic", "DB_PASSWORD", os.environ.get("DB_PASSWORD")
        )
    config.set_section_option("alembic", "DB_HOST", os.environ.get("DB_HOST"))

    alembic_config = config.get_section(config.config_ini_section)
    connectable = engine_from_config(
        alembic_config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    target_metadata = BaseEnv.make_target_metadata()
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
