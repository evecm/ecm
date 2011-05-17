import os, sys

install_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(install_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'ecm.settings'


import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
