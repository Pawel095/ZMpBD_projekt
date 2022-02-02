FROM python:3.10-slim as py3

WORKDIR /app

RUN pip install --upgrade pip setuptools poetry
RUN poetry config virtualenvs.create false
COPY poetry.lock /app
COPY pyproject.toml /app
RUN poetry install --no-dev

FROM openjdk:8-slim
COPY --from=py3 / /

RUN apt-get update && apt-get install -y wait-for-it

WORKDIR /app
COPY . /app
RUN chmod +x ./entrypoint.sh
RUN poetry install --no-dev
RUN predownloadJars
RUN buildModel

COPY . /app
