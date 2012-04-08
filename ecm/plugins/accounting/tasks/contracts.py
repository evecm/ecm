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
from ecm.apps.common.models import UpdateDate
from ecm.utils import tools

__date__ = "2012 04 05"
__author__ = "tash"


import logging
from datetime import datetime

from django.db import transaction

from ecm.apps.eve import api

from ecm.plugins.accounting.models import Contract, ContractItem

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def update():
    """
    Update all contracts 
    """
    LOG.info("fetching /corp/Contracts.xml.aspx...")
    # Connect to EVE API
    api_conn = api.connect()
    contractsApi = api_conn.corp.Contracts()
    # checkApiVersion(contractsApi._meta.version)

    current_time = contractsApi._meta.currentTime
    cached_until = contractsApi._meta.cachedUntil
    LOG.debug("current time : %s", str(current_time))
    LOG.debug("cached util : %s", str(cached_until))
    LOG.debug("parsing api response...")

    processContracts(contractsApi.contractList, api_conn)
    UpdateDate.mark_updated(model=Contract, date=datetime.now())

def processContracts(contract_list, connection):
    # Get old contracts
    old_contracts = {}
    for contract in Contract.objects.all():
        old_contracts[contract] = contract

    # Get new contracts
    new_contracts = {}
    for entry in contract_list:
        contract = create_contract_fom_row(entry)
        new_contracts[contract] = contract

    removed_contracts, added_contracts = tools.diff(old_contracts, new_contracts)

    # Query the contract items
    old_items = {}
    for item in ContractItem.objects.all():
        old_items[item] = item
    
    new_items = {}
    
    #for contract in added_contracts:
    #    items_api = connection.corp.ContractItems(contractID=contract.contractID)
    #    checkApiVersion(items_api._meta.version)
    #    item_list = items_api.itemList
    #    for item in item_list:
    #        new_item = create_contract_item(item, contract)
    #        new_items[new_item] = new_item
    
    #removed_items, added_items = tools.diff(old_items, new_items)

    write_contracts(added_contracts, removed_contracts)
    #write_contract_items(added_items, removed_items)
    

@transaction.commit_on_success
def write_contracts(new_contracts, old_contracts):
    """
    Write the API results
    """
    if len(old_contracts) > 0:
        Contract.objects.all().delete()
        LOG.info("%d old contracts removed." % len(old_contracts))
    for contract in new_contracts:
        contract.save()
    LOG.info("%d new contracts added." % len(new_contracts))

def write_contract_items(new_items, old_items):
    """
    Write the API results
    """
    if len(old_items) > 0:
        ContractItem.objects.all().delete()
        LOG.info("%d old contract items removed." % len(old_items))
    for item in new_items:
        item.save()
    LOG.info("%d new contract items added." % len(new_items))

def create_contract_fom_row(row):
    return Contract(contractID=row.contractID,
                    issuerID=row.issuerID,
                    issuerCorpID=row.issuerCorpID,
                    assigneeID=row.assigneeID,
                    acceptorID=row.acceptorID,
                    startStationID=row.startStationID,
                    endStationID=row.endStationID,
                    type=row.type,
                    status=row.status,
                    title=row.title,
                    forCorp=row.forCorp,
                    availability=row.availability,
                    dateIssued=row.dateIssued,
                    dateExpired=row.dateExpired,
                    dateAccepted=row.dateAccepted,
                    numDays=row.numDays,
                    dateCompleted=row.dateCompleted,
                    price=row.price,
                    reward=row.reward,
                    collateral=row.collateral,
                    buyout=row.buyout,
                    volume=row.volume)

def create_contract_item(entry, contract):
    return ContractItem(contract_id=contract.contractID,
                        recordID=entry.recordID,
                        typeID=entry.typeID,
                        quantity=entry.quantity,
                        rawQuantity=entry.rawQuantity,
                        singleton=entry.singleton,
                        included=entry.included)
