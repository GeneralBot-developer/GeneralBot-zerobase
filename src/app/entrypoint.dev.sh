set -eu
echo "Setting up environment..."
cd alembic
python3 -m alembic upgrade head
python3 -m alembic revision --autogenerate
python3 -m alembic upgrade head
cd ..
nodemon --signal SIGINT -e py,ini --exec python -m GBot