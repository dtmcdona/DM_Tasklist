FROM python:3.11.0a4-alpine3.15
MAINTAINER dtmdona

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app
RUN python3 -m venv /app/venv
ENV PATH="/home/usr/.local/bin:${PATH}"
COPY ./app /app
RUN source venv/bin/activate
RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install psycopg2-binary
RUN apk add zlib-dev jpeg-dev gcc musl-dev
RUN pip install -r requirements.txt

RUN adduser -D usr
USER usr