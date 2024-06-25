
FROM python:3.7-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  # LDAP dependencies
  && apt-get install -y libldap2-dev libsasl2-dev ldap-utils \
  # for nvm install
  && apt-get install -y wget \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

RUN addgroup --system django \
  && adduser --system --ingroup django django

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install -U pip
RUN pip install --no-cache-dir -r /requirements/production.txt \
  && rm -rf /requirements

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint
RUN chown django /entrypoint

COPY ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
RUN chown django /start
COPY --chown=django:django . /app

# install npm
SHELL ["/bin/bash", "--login", "-c"]
WORKDIR /app
RUN rm -rf node_modules && mkdir node_modules
RUN wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
RUN nvm install v16.15.1 
# not sure why npm ci runs successfully but the starting container can't find node_modules!
RUN npm ci

# GN: Fix static & media volume permission
# RUN chmod ugo+rwX . && chown django:django .
# RUN mkdir -p /app/cotr/media /app/node_modules && chmod -R ugo+rwX /app/cotr/media /app/cotr/media /app/staticfiles /app/node_modules && chown -R django:django /app/cotr/media /app/staticfiles /app/node_modules

USER django

WORKDIR /app

ENTRYPOINT ["/entrypoint"]
