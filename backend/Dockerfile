FROM python:3.10-slim

WORKDIR /app

RUN pip install --upgrade pip setuptools poetry
RUN poetry config virtualenvs.create false
COPY poetry.lock /app
COPY pyproject.toml /app
RUN poetry install --no-dev
RUN apt-get update && apt-get install -y wait-for-it

COPY . /app
RUN chmod +x ./entrypoint.sh
RUN poetry install --no-dev

ENTRYPOINT [ "/app/entrypoint.sh" ]