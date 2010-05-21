#!/usr/bin/env python
'''
This file is part of ICE Security Management

Created on 17 mai 2010
@author: diabeteman
'''

import setenv

# imports and code below

from ism.core.parsers import corp

from datetime import datetime

print datetime.now().strftime("%Y-%m-%d ~ %H:%M:%S") + " [ISM] " + corp.update()

