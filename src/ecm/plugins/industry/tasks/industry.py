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

from ecm.core import evecentral, utils
from ecm.plugins.industry.models import Supply, SupplySource

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update_supply_prices():
    supplyPrices = Supply.objects.filter(autoUpdate=True)
    for supplySource in SupplySource.objects.all():
        logger.debug('Updating supply prices for %s...' % supplySource.name)
        prices = supplyPrices.filter(supplySource=supplySource)
        itemIDs = prices.values_list('typeID', flat=True)
        buyPrices = evecentral.get_buy_prices(itemIDs, supplySource.locationID)

        for supPrice in prices:
            if buyPrices[supPrice.typeID] > 0.0 and supPrice.price != buyPrices[supPrice.typeID]:
                supPrice.updatePrice(buyPrices[supPrice.typeID])
                logger.info('New price for "%s" -> %s' % (supPrice.item_admin_display(),
                                                          utils.print_float(buyPrices[supPrice.typeID])))
