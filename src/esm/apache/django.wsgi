import os, os.path
import sys

apache_dir = os.path.abspath(os.path.dirname(__file__))
install_dir = os.path.join(apache_dir, "../../")
sys.path.append(install_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'ism.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
