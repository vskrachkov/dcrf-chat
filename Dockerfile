FROM python:3.9-alpine
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /data
COPY Pipfile* /data/

RUN set -eux \
    && apk update \
    && apk upgrade \
    && apk add --update --virtual .build-deps postgresql-dev build-base gettext libressl-dev musl-dev libffi-dev \
    && apk add --update libpq postgresql-client \
    && pip3 install pip==21.1.2 \
    && pip3 install --no-cache-dir pipenv==2021.5.29 \
    && pipenv install --system --deploy --ignore-pipfile --clear \
    && apk del .build-deps \
    && pipenv --clear \
    && pip3 uninstall pipenv -y

COPY src/. /data/

USER nobody
CMD uvicorn asgi:application --proxy-headers --forwarded-allow-ips "*" --host 0.0.0.0 --port 8000 --log-level warning