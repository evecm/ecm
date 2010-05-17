#!/usr/bin/env python
'''
This file is part of ICE Security Management

Created on 17 mai 2010
@author: diabeteman
'''


import os, sys
sys.path.append('/path/to/') # the parent directory of the project
sys.path.append('/path/to/project') # these lines only needed if not on path
os.environ['DJANGO_SETTINGS_MODULE'] = 'ism.settings'

# imports and code below