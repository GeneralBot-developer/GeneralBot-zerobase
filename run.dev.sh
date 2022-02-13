#!/bin/sh
#code1
set -eu
pipenv install
python -m pip install python-dotenv
python -m pip install alembic
alembic -c alembic.dev.ini upgrade head
alembic -c ./alembic.dev.ini revision --autogenerate
alembic -c alembic.dev.ini upgrade head
python3 -m GBot