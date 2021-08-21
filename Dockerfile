FROM python:3.7-alpine
MAINTAINER Italo Carvalho

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
# --no-cache serve para reduzir arquivos extras
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

# segurança
RUN adduser -D user
USER user