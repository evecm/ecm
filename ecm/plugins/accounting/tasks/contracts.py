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

from django.db import transaction
from django.utils import timezone

from ecm.apps.common import api
from ecm.apps.corp.models import Corporation
from ecm.apps.common.models import UpdateDate
from ecm.utils import tools
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
    LOG.debug("Fetching Contracts...")
    contractsApi = api_conn.corp.Contracts()

    current_time = timezone.make_aware(contractsApi._meta.currentTime, timezone.utc)
    cached_until = timezone.make_aware(contractsApi._meta.cachedUntil, timezone.utc)
    LOG.debug("current time : %s", str(current_time))
    LOG.debug("cached util : %s", str(cached_until))
    LOG.debug("parsing api response...")
    
    process_contracts(contractsApi.contractList, api_conn)
    UpdateDate.mark_updated(model=Contract, date=timezone.now())

#------------------------------------------------------------------------------
def process_contracts(contract_list, connection):
    """
    Process all contracts from the API
    """
    try:
        alliance_id = Corporation.objects.mine().alliance.allianceID
    except AttributeError:
        alliance_id = 0
    LOG.debug("Fetching contracts from DB...")    
    # Get old contracts
    old_contracts = {}
    for contract in Contract.objects.all():
        old_contracts[contract] = contract
    LOG.debug("%s contracts found in DB..." % len(old_contracts))
    
    # Get new contracts
    LOG.debug("Fetching contracts from API...")   
    new_contracts = {}
    for entry in contract_list:
        if entry.assigneeID != alliance_id:
            contract = populate_contract(entry)
            new_contracts[contract] = contract
    
    # Get changes
    removed_contracts, added_contracts = tools.diff(old_items=old_contracts, new_items=new_contracts)
    LOG.debug("Contracts from API: %s" % len(new_contracts))
    LOG.debug("Removed contracts: %s" % len(removed_contracts))
    LOG.debug("Added contracts: %s" % len(added_contracts))
    
    # Query the contract items
    old_items = {}
    for item in ContractItem.objects.all():
        old_items[item] = item

    # Note: We dont need to diff items, since they are contained in contracts
    # Get new items by contractID from EVE API
    new_items = {}
    for contract in added_contracts:
        if contract.type != 2: # 'Courier' No items for courier contracts from API
            try:
                items_api = connection.corp.ContractItems(contractID=contract.contractID)
                item_list = items_api.itemList
                LOG.debug("%s items for contract id %s..." % (len(item_list), contract.contractID))
                for item in item_list:
                    new_item = populate_contract_item(item, contract)
                    new_items[new_item] = new_item
            except api.RequestError:
                LOG.debug("Invalid or missing contractID: %s" % contract.contractID)
            except RuntimeError:
                LOG.debug("Unable to fetch items for contract ID: %s" % contract.contractID)
                continue
    # Get all contractitem ids for removed contracts
    removed_items = []
    for contract in removed_contracts:
        removed_items.append(ContractItem.objects.filter(contract=contract))
    
    LOG.debug("Writing contracts to DB...")
    write_contracts(added_contracts, removed_contracts)
    LOG.debug("Writing contract items to DB...")
    write_contract_items(new_items, removed_items)
    update_contract_data(old_contracts, new_contracts)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def write_contracts(new_contracts, old_contracts):
    """
    Write the API results
    """
    try:
        for contract in old_contracts:
            contract.delete()
        LOG.info("%d old contracts removed." % len(old_contracts))
        for contract in new_contracts:
            contract.save()
        LOG.info("%d new contracts added." % len(new_contracts))
    except:
        print contract.__dict__
        raise

#------------------------------------------------------------------------------
@transaction.commit_on_success
def write_contract_items(new_items, old_items):
    """
    Write the API results for contract items to DB.
    """
    try:
        if len(old_items) > 0:
            for item in old_items:
                item.delete()
            LOG.info("%d old contract items removed." % len(old_items))
        for item in new_items:
            item.save()
        LOG.info("%d new contract items added." % len(new_items))
    except:
        print item.__dict__
        raise

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update_contract_data(old_contracts, new_contracts):
    """
    Write updated status and other data (dates, acceptedID) to DB if status has changed.
    """
    # Do a union of the old (DB) contracts with the new (API) contracts
    # using viewkeys() would be more efficient here but requires Python 2.7+.  Ref http://stackoverflow.com/a/18554081
    for existing_contract in set(old_contracts.keys()) & set(new_contracts.keys()):
        if old_contracts[existing_contract].status != new_contracts[existing_contract].status:
            LOG.debug("Contract %d changing state: %s -> %s" % (existing_contract.contractID, old_contracts[existing_contract].status_string(), new_contracts[existing_contract].status_string()))
            new_contracts[existing_contract].save()

#------------------------------------------------------------------------------
def populate_contract(row):
    """
    Takes a contract row from the API resultset and creates a Contract object.
    """
    try:
        contract_status = Contract.STATUS_KEYS[row.status]
    except KeyError:
        contract_status = -1 # unknown
    
    try:
        contract_type = Contract.TYPE_KEYS[row.type]
    except KeyError:
        contract_type = -1 # unknown
        
    try:
        contract_availability = Contract.AVAILABILITY_KEYS[row.availability]
    except KeyError:
        contract_availability = -1 # unknown
    
    try:
        row.dateIssued = timezone.make_aware(row.dateIssued, timezone.utc)
    except AttributeError:
        row.dateIssued = None
    try:
        row.dateAccepted = timezone.make_aware(row.dateAccepted, timezone.utc)
    except AttributeError:
        row.dateAccepted = None
    try:
        row.dateCompleted = timezone.make_aware(row.dateCompleted, timezone.utc)
    except AttributeError:
        row.dateCompleted = None
    try:
        row.dateExpired = timezone.make_aware(row.dateExpired, timezone.utc)
    except AttributeError:
        row.dateExpired = None
    return Contract(contractID=row.contractID,
                    issuerID=row.issuerID,
                    issuerCorpID=row.issuerCorpID,
                    assigneeID=row.assigneeID,
                    acceptorID=row.acceptorID,
                    startStationID=row.startStationID,
                    endStationID=row.endStationID,
                    type=contract_type,
                    status=contract_status,
                    title=row.title,
                    forCorp=bool(row.forCorp),
                    availability=contract_availability,
                    dateIssued=row.dateIssued,
                    dateExpired=row.dateExpired,
                    dateAccepted=row.dateAccepted,
                    dateCompleted=row.dateCompleted,
                    numDays=row.numDays,
                    price=row.price,
                    reward=row.reward,
                    collateral=row.collateral,
                    buyout=row.buyout,
                    volume=row.volume)

#------------------------------------------------------------------------------
def populate_contract_item(entry, contract):
    """
    Takes a contract item row from the API ResultSet and creates a ContractItem object.
    """
    if entry.rawQuantity:
        raw_quantity = entry.rawQuantity
    else:
        raw_quantity = 0
    return ContractItem(contract_id=contract.contractID,
                        recordID=entry.recordID,
                        typeID=entry.typeID,
                        quantity=entry.quantity,
                        rawQuantity=raw_quantity,
                        singleton=entry.singleton,
                        included=entry.included)
