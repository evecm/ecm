#!/bin/bash

# this script allows to run ECM into "gunicorn" WSGI server monitored through "runit".
# see http://code.google.com/p/eve-corp-management/wiki/InstallationInstructions#gunicorn_with_asynchronous_gevent_workers
# for more information.

CUR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

DJANGO_SETTINGS="$CUR_DIR/../ecm/settings.py"
GUNICORN_SETTINGS="$CUR_DIR/gunicorn_settings_example.py"

exec gunicorn_django -c "$GUNICORN_SETTINGS" "$DJANGO_SETTINGS"

