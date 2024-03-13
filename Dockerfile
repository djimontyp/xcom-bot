FROM python:3.11.4-slim as python-layer
ENV PYTHONUNBUFFERED=true

WORKDIR /xcom
COPY src ./src
COPY requirements.txt ./
COPY ".env" ./.env
COPY alembic.ini ./alembic.ini

RUN pip install -r ./requirements.txt
