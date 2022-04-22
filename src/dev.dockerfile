FROM python:3.8 as builder
WORKDIR /bot
RUN apt-get update -y && \
    apt-get upgrade -y
COPY ./app/Pipfile ./app/Pipfile.lock /bot/
RUN pip install pipenv && \
    pipenv install --system

FROM python:3.8-slim
WORKDIR /bot
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y nodejs npm curl && \
    npm install -g n && \
    n stable && \
    apt-get update -y && \
    apt-get purge -y nodejs npm && \
    apt-get install -y ffmpeg && \
    apt-get autoremove -y
RUN npm install -g nodemon

ENV PATH $PATH:/usr/bin/alembic
ENV PYTHONBUFFERED=1
COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages

COPY . /bot
RUN pip install alembic
RUN pip install cryptography
