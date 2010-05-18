import os
import sys

sys.path.append('/var/django')
sys.path.append('/var/django/ism')
sys.path.append('/usr/local/lib/python2.6/dist-packages')
sys.path.append('/usr/local/lib/python2.6/dist-packages/django')

os.environ['DJANGO_SETTINGS_MODULE'] = 'ism.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
