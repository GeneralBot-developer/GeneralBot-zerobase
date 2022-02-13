#!/bin/sh
#code1
set -eu
pip install pipenv
pipenv install
python -m pip install python-dotenv
python -m pip install alembic
alembic -c alembic.prod.ini upgrade head
alembic -c ./alembic.prod.ini revision --autogenerate
alembic -c alembic.prod.ini upgrade head
python3 -m GBot