# Copyright (c) 2010-2012 Robin Jarry
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

from ecm.apps.common.models import Setting

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def get_buy_prices(item_ids, systemID):

    prices = {}
    for i in range(len(item_ids)//50+1):
        params=[]
        for item_id in item_ids[i*50:(i+1)*50]:
            params.append(("typeid", item_id))
        params.append(("minQ", 10))
        if systemID != 1:
            params.append(("usesystem", systemID))
        evecentralurl = Setting.get('industry_evecentral_url')
        url = evecentralurl + '?' + urllib.urlencode(params)
        logger.info('Fetching market info from %s...' % url)
        response = urllib2.urlopen(url)
        element = ElementTree.parse(source=response)
        for typ in element.findall('.//type'):
            typeID = int(typ.attrib['id'])
            buyMax = typ.find('buy/max')
            if buyMax is not None:
                prices[typeID] = round(float(buyMax.text), 2)
    return prices
