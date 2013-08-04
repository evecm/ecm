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

__date__ = "2012 4 19"
__author__ = "Ajurna"

#import logging
import urllib2

from ecm.utils import _json as json
#logger = logging.getLogger(__name__)


#------------------------------------------------------------------------------
def get_buy_prices(item_ids, systemID):
    'http://www.evemarketeer.com/api/info/34/json/10000043/buy_highest5'
    prices = {}
    for item in item_ids:
            
        if systemID == 1:
            systemID = 10000002
            
        evemarketeerurl = 'http://www.evemarketeer.com/api/info/'
        url = evemarketeerurl + str(item) +'/json/' + str(systemID) + '/buy_highest5'
        #logger.debug('Fetching market info from %s...' % url)
        response = urllib2.urlopen(url)
        price = json.load(response)
        prices[item] = price[0]['buy_highest5']
    return prices
