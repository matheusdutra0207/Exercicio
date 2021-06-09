FROM python:3.7-alpine

COPY . /app
WORKDIR /app

RUN pip install protobuf && \
    pip install --upgrade google && \
    pip install is-msgs && \
    pip install is-wire && \
    pip install celery && \
    pip install --upgrade protobuf
