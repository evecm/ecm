

import os
from os import path
import imp
import logging
from ecm.settings import PLUGIN_APPS

LOG = logging.getLogger(__name__)

DICT = {}
LIST = []

class ECMPlugin(object):

    def __init__(self, package):
        self.package = package
        self.app_prefix = package.rsplit('.', 1)[-1]
        self.urlconf = package + '.urls'
        self.menu_module = __import__(package + '.menu', fromlist=[package])
        self.menu = self.menu_module.ECM_MENUS


for app in PLUGIN_APPS:
    DICT[app] = ECMPlugin(package=app)
    LIST.append(DICT[app])
