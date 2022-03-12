#!/bin/sh
#code1
set -eu
alembic -c alembic.dev.ini upgrade head
alembic -c ./alembic.dev.ini revision --autogenerate
alembic -c alembic.dev.ini upgrade head
python3 -m GBot