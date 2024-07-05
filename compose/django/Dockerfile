FROM node:10-stretch-slim AS image-npm

RUN mkdir /node
WORKDIR /node
COPY ./volumes/cotr/package*.json /node/
RUN npm ci && npm cache clean --force
RUN tar czf node_modules.tar.gz node_modules

FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  && apt-get install -y libldap2-dev libsasl2-dev ldap-utils \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Requirements are installed here to ensure they will be cached.
COPY ./volumes/cotr/requirements.txt /tmp/requirements.txt
RUN pip install -U pip \
  && pip install -r /tmp/requirements.txt

COPY ./compose/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

WORKDIR /app

COPY --from=image-npm /node/node_modules.tar.gz /

ENTRYPOINT ["/entrypoint"]
