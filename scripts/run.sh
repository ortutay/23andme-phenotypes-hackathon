#!/usr/bin/env bash

set -xe

# Activate virtualenv
source /app/venv/bin/activate

# Env vars for all environments
export DJANGO_DEBUG=False
export DJANGO_SETTINGS_MODULE=config.settings.production
export DJANGO_LOG_DIR=/var/log/app
export NEW_RELIC_CONFIG_FILE=/app/newrelic.ini
export RECAPTCHA_PUBLIC_KEY=6LfxeSUTAAAAAPWd6rYaD3UVp76CeGRajg6IuCxX

./manage.py check --deploy
newrelic-admin run-program gunicorn config.wsgi:application --config config/gunicorn.py
