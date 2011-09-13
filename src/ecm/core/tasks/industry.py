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

from django.db import transaction
from django.conf import settings

from ecm.core import evecentral
from ecm.data.industry.models import SupplyPrice

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update_supply_prices():
    logger.debug('Updating supply prices...')
    supplyPrices = SupplyPrice.objects.filter(autoUpdate=True)
    itemIDs = supplyPrices.values_list('typeID', flat=True)
    buyPrices = evecentral.get_buy_prices(itemIDs, settings.EVE_CENTRAL_BUY_SOURCE)
    for supPrice in supplyPrices:
        if buyPrices[supPrice.typeID] > 0.0 and supPrice.price != buyPrices[supPrice.typeID]:
            logger.info('New price for "%s" : %f' % (supPrice.item_admin_display(), buyPrices[supPrice.typeID]))
            supPrice.price = buyPrices[supPrice.typeID]
            supPrice.save()
    