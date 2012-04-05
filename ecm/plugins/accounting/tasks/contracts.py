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

__date__ = "2012 04 05"
__author__ = "tash"


import logging
from datetime import datetime

from django.db import transaction

from ecm.apps.eve import api
from ecm.lib import eveapi

# from ecm.apps.corp.models import Wallet
from ecm.core.parsers import markUpdated, checkApiVersion
from ecm.plugins.accounting.tasks import fix_encoding
from ecm.plugins.accounting.models import Contract

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def update():
    """
    Updates all contracts 
    """
    LOG.info("fetching /corp/Contracts.xml.aspx...")
    # Connect to EVE API
    apiConn = api.connect()
    contractsApi = apiConn.corp.Contracts()
    checkApiVersion(contractsApi._meta.version)

    currentTime = contractsApi._meta.currentTime
    cachedUntil = contractsApi._meta.cachedUntil
    LOG.debug("current time : %s", str(currentTime))
    LOG.debug("cached util : %s", str(cachedUntil))
    LOG.debug("parsing api response...")
    entries = list(contractsApi.contractList)
    write_results(entries)

def write_results(entries):
    """
    Write the API results
    """
    for e in entries:
        Contract.objects.create(contractID = e.contractID,
                                issuerID = e.issuerID,
                                issuerCorpID = e.issuerCorpID,
                                assigneeID = e.assigneeID,
                                acceptorID = e.acceptorID,
                                startStationID = e.startStationID,
                                endStationID = e.endStationID,
                                type = e.type,
                                status = e.status,
                                title = e.title,
                                forCorp = e.forCorp,
                                availability = e.availability,
                                dateIssued = e.dateIssued,
                                dateExpired = e.dateExpired,
                                dateAccepted = e.dateAccepted,
                                numDays = e.numDays,
                                dateCompleted = e.dateCompleted,
                                price = e.price,
                                reward = e.reward,
                                collateral = e.collateral,
                                buyout = e.buyout,
                                volume = e.volume)
    LOG.info("%d contracts added." % len(entries))
        
