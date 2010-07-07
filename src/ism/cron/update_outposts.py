#!/usr/bin/env python
'''
This file is part of ICE Security Management

Created on 17 mai 2010
@author: diabeteman
'''

import setenv

# imports and code below

from ism.core.parsers import outposts

from datetime import datetime
from ism.core.db import CACHE_TYPES

print datetime.now().strftime("%Y-%m-%d ~ %H:%M:%S") + " [ISM] " + outposts.update()
CACHE_TYPES.clear()