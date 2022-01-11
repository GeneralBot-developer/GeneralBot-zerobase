#!/bin/sh
#code1
set -eu
pipenv install
python -m pip install python-dotenv
python -m pip install alembic
cd alembic
alembic upgrade head
alembic revision --autogenerate
alembic upgrade head
cd ..
python3 -m GBot