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

__date__ = "2012 04 06"
__author__ = "tash"


import logging
from django.db import transaction

from ecm.utils import tools
from ecm.apps.common.models import UpdateDate
from ecm.apps.common import api
from ecm.plugins.accounting.models import MarketOrder
from django.utils import timezone

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def update():
    """
    Update all orders
    """
    LOG.info("fetching /corp/MarketOrders.xml.aspx...")
    # Connect to EVE API
    api_conn = api.connect()
    ordersApi = api_conn.corp.MarketOrders()
    # checkApiVersion(ordersApi._meta.version)

    LOG.debug("parsing api response...")

    processOrders(ordersApi.orders, api_conn)
    UpdateDate.mark_updated(model=MarketOrder, date=timezone.now())

def processOrders(orders, connection):
    # Get old Orders
    old_orders = {}
    for order in MarketOrder.objects.all():
        old_orders[order] = order

    # Get new orders
    new_orders = {}
    for entry in orders:
        order = create_order_fom_row(entry)
        new_orders[order] = order

    removed_orders, added_orders = tools.diff(old_orders, new_orders)
    write_orders(added_orders, removed_orders)


@transaction.commit_on_success
def write_orders(new_orders, old_orders):
    """
    Write the API results
    """
    if len(old_orders) > 0:
        MarketOrder.objects.all().delete()
        LOG.info("%d old orders removed." % len(old_orders))
    for order in new_orders:
        order.save()
    LOG.info("%d new orders added." % len(new_orders))

def create_order_fom_row(row):
    row.issued = timezone.make_aware(row.issued, timezone.utc) # make issue date tz aware. use utc.
    return MarketOrder(orderID = row.orderID,
                       charID = row.charID,
                       stationID = row.stationID,
                       volEntered = row.volEntered,
                       volRemaining = row.volRemaining,
                       minVolume = row.minVolume,
                       orderState = row.orderState,
                       typeID = row.typeID,
                       range = row.range,
                       accountKey_id = row.accountKey,
                       duration = row.duration,
                       escrow = row.escrow,
                       price = row.price,
                       bid = row.bid,
                       issued = row.issued)
