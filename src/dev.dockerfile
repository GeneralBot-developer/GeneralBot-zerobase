FROM python:3.8 as builder
WORKDIR /bot
RUN apt update -y && \
    apt upgrade -y
COPY ./app/Pipfile ./app/Pipfile.lock /bot/
RUN pip install pipenv && \
    pipenv install --system

FROM python:3.8-slim
WORKDIR /bot
RUN apt update -y && \
    apt upgrade -y && \
    apt install -y nodejs npm curl && \
    npm install -g n && \
    n stable && \
    apt purge -y nodejs npm && \
    apt install -y ffmpeg && \
    apt autoremove -y
RUN npm install -g nodemon

ENV PYTHONBUFFERED=1
COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages

COPY . /bot
RUN pip install alembic