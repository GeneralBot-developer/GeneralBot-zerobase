pipenv install
pipenv shell
alembic upgrade head
alembic revision --autogenerate
alembic upgrade head
nodemon --signal SIGINT -e py,ini --exec python -m GBot