#!/usr/bin/env python
'''
This file is part of ICE Security Management

Created on 17 mai 2010
@author: diabeteman
'''

import setenv

# imports and code below

from ism.core.parsers import membersecu
from ism.data.roles.models import Member
from datetime import datetime


logString = datetime.now().strftime("%Y-%m-%d ~ %H:%M:%S") + " [ISM] " + membersecu.update()

print logString

