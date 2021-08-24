FROM python:3.7-alpine
LABEL org.opencontainers.image.authors="italocarvalhoti@hotmail.com"
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
# --no-cache serve para reduzir arquivos extras
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

# segurança
RUN adduser -D user
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web
USER user