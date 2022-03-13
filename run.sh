#!/bin/sh
#code1
set -eu
git pull origin master
pipenv install
alembic -c alembic.prod.ini upgrade head
alembic -c ./alembic.prod.ini revision --autogenerate
alembic -c alembic.prod.ini upgrade head
python3 -m GBot