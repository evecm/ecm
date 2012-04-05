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
from ecm.core.parsers import diff, markUpdated, checkApiVersion
from ecm.plugins.accounting.tasks import fix_encoding
from ecm.plugins.accounting.models import Contract

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def update():
    """
    Update all contracts 
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

    entries = contractsApi.contractList

    # Get old contracts
    oldContracts = {}
    for contract in Contract.objects.all():
        oldContracts[contract] = contract

    # Get new contracts
    newContracts = {}
    for entry in entries:
        contract = create_contract_fom_row(entry)
        newContracts[contract] = contract

    removedContracts, addedContracts = diff(oldContracts, newContracts)
    write_results(addedContracts, removedContracts)
    markUpdated(model=Contract, date=datetime.now())

@transaction.commit_on_success
def write_results(newContracts, oldContracts):
    """
    Write the API results
    """
    if len(oldContracts) > 0:
        Contract.objects.all().delete()
        LOG.info("%d old contracts removed." % len(oldContracts))
    for contract in newContracts:
        contract.save()
    LOG.info("%d contracts added." % len(newContracts))

def create_contract_fom_row(row):
    return Contract(contractID = row.contractID,
                    issuerID = row.issuerID,
                    issuerCorpID = row.issuerCorpID,
                    assigneeID = row.assigneeID,
                    acceptorID = row.acceptorID,
                    startStationID = row.startStationID,
                    endStationID = row.endStationID,
                    type = row.type,
                    status = row.status,
                    title = row.title,
                    forCorp = row.forCorp,
                    availability = row.availability,
                    dateIssued = row.dateIssued,
                    dateExpired = row.dateExpired,
                    dateAccepted = row.dateAccepted,
                    numDays = row.numDays,
                    dateCompleted = row.dateCompleted,
                    price = row.price,
                    reward = row.reward,
                    collateral = row.collateral,
                    buyout = row.buyout,
                    volume = row.volume)

