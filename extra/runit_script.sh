#!/bin/bash

# this script allows to run ECM into "gunicorn" WSGI server monitored through "runit".
# see http://code.google.com/p/eve-corp-management/wiki/InstallationInstructions#gunicorn_with_asynchronous_gevent_workers
# for more information.

ECM_INSTALL_DIR=/srv/eve-corp-management

DJANGO_SETTINGS="$ECM_INSTALL_DIR/ecm/settings.py"
GUNICORN_SETTINGS="$ECM_INSTALL_DIR/scripts/gunicorn_settings_example.py"

exec gunicorn_django -c "$GUNICORN_SETTINGS" "$DJANGO_SETTINGS"

