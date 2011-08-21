# Copyright (c) 2010-2011 Robin Jarry
# 
# This file is part of EVE Corporation Management.
# 
# EVE Corporation Management is free software: you can redistribute it and/or 
# modify it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or (at your 
# option) any later version.
# 
# EVE Corporation Management is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
# more details.
# 
# You should have received a copy of the GNU General Public License along with 
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

__date__ = "2011 8 20"
__author__ = "diabeteman"

import logging
import urllib
import urllib2
from xml.etree import ElementTree

from django.conf import settings

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def get_buy_prices(itemIDs, systemID=None):
    
    params=[]
    for id in itemIDs:
        params.append(("typeid", id))
    params.append(("minQ", 1000))
    if systemID:
        params.append(("usesystem", systemID))
    url = settings.EVE_CENTRAL_URL + '?' + urllib.urlencode(params)
    logger.info('Fetching market info from %s...' % url)
    response = urllib2.urlopen(url)
    element = ElementTree.parse(source=response)
    prices = {}
    for type in element.findall('.//type'):
        typeID = int(type.attrib['id'])
        buyMax = type.find('buy/max')
        if buyMax is not None:
            prices[typeID] = round(float(buyMax.text), 2)
    return prices