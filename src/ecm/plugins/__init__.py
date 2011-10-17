

import os
from os import path
import imp
import logging
from ecm.settings import list_plugin_apps

LOG = logging.getLogger(__name__)

def app_urls():
    urls = []
    for plugin in list_plugin_apps():
        app_prefix = plugin.rsplit('.', 1)[-1]
        urlconf = plugin + '.urls'
        urls.append( (app_prefix, urlconf) )
    return urls

def app_menus():
    menus = []
    for app in list_plugin_apps():
        m = __import__(app + '.menu', fromlist=[app])
        menus.append(getattr(m, 'ECM_MENUS'))
    return menus

URLS = app_urls()
MENUS = app_menus()
