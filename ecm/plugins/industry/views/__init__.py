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

__date__ = "2015 1 21"
__author__ = "diabeteman"

import logging
import time

from django.db import transaction
from django.shortcuts import render_to_response
from django.template.context import RequestContext as Ctx

from ecm.utils import tools
from ecm.plugins.industry.models.catalog import ItemGroup
from ecm.apps.eve.models import Type, BlueprintReq
from ecm.apps.eve import constants
from ecm.plugins.industry.models import CatalogEntry, Supply

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def home(request):
    return render_to_response('ecm/industry/industry_home.html', {}, Ctx(request))


#------------------------------------------------------------------------------
@transaction.commit_on_success
def create_missing_catalog_entries():
    start = time.time()
    manufacturable_types = Type.objects.filter(blueprint__isnull=False,
                                               published=1,
                                               metaGroupID__in=constants.MANUFACTURABLE_ITEMS,
                                               market_group__isnull=False)
    manufacturable_types = manufacturable_types.exclude(typeID__in=constants.FACTION_FRIGATES_TYPEIDS)
    eve_typeIDs = set(manufacturable_types.values_list('typeID', flat=True))
    ecm_typeIDs = set(CatalogEntry.objects.values_list('typeID', flat=True))

    missing_ids = list(eve_typeIDs - ecm_typeIDs)

    for sublist in tools.sublists(missing_ids, 50):
        for obj in Type.objects.filter(typeID__in=sublist):
            CatalogEntry.objects.create(typeID=obj.typeID, typeName=obj.typeName, is_available=False)

    if missing_ids:
        duration = time.time() - start
        logger.info('added %d missing catalog entries (took %.2f sec.)', len(missing_ids), duration)
create_missing_catalog_entries()

#------------------------------------------------------------------------------
@transaction.commit_on_success
def create_missing_supplies():
    start = time.time()
    eve_supplies = BlueprintReq.objects.filter(required_type__blueprint__isnull=True,
                                               required_type__published=1)
    eve_typeIDs = set(eve_supplies.values_list('required_type', flat=True).distinct())
    ecm_typeIDs = set(Supply.objects.values_list('typeID', flat=True))

    missing_ids = eve_typeIDs - ecm_typeIDs

    for typeID in missing_ids:
        Supply.objects.create(typeID=typeID)

    if missing_ids:
        duration = time.time() - start
        logger.info('added %d missing supplies (took %.2f sec.)', len(missing_ids), duration)
create_missing_supplies()

#------------------------------------------------------------------------------
@transaction.commit_on_success
def create_missing_item_groups():
    start = time.time()
    all_types = Type.objects.filter(blueprint__isnull=False,
                                    published=1,
                                    metaGroupID__in=constants.MANUFACTURABLE_ITEMS,
                                    market_group__isnull=False)
    all_types = all_types.exclude(typeID__in=constants.FACTION_FRIGATES_TYPEIDS)
    
    t1_items_group, _ = ItemGroup.objects.get_or_create(name='Tech 1 Items')
    t2_items_group, _ = ItemGroup.objects.get_or_create(name='Tech 2 Items')
    t3_items_group, _ = ItemGroup.objects.get_or_create(name='Tech 3 Items')
    
    t1_ships_group, _ = ItemGroup.objects.get_or_create(name='Tech 1 Ships')
    t2_ships_group, _ = ItemGroup.objects.get_or_create(name='Tech 2 Ships')
    t3_ships_group, _ = ItemGroup.objects.get_or_create(name='Tech 3 Ships')
    
    t1_modules_group, _ = ItemGroup.objects.get_or_create(name='Tech 1 Modules')
    t2_modules_group, _ = ItemGroup.objects.get_or_create(name='Tech 2 Modules')
    t3_modules_group, _ = ItemGroup.objects.get_or_create(name='Tech 3 Modules')
    
    charges_group, _ = ItemGroup.objects.get_or_create(name='Charges')
    capital_ships_group, _ = ItemGroup.objects.get_or_create(name='Capital Ships')
    
    
    t1_items = all_types.filter(metaGroupID=1)
    t2_items = all_types.filter(metaGroupID=2)
    t3_items = all_types.filter(metaGroupID=14) # T3 metaGroup is 14
    
    t1_ships = t1_items.filter(category=constants.SHIP_CATEGORYID)
    t2_ships = t2_items.filter(category=constants.SHIP_CATEGORYID)
    t3_ships = t3_items.filter(category=constants.SHIP_CATEGORYID)
    
    t1_modules = t1_items.filter(category=constants.MODULE_CATEGORYID)
    t2_modules = t2_items.filter(category=constants.MODULE_CATEGORYID)
    t3_modules = t3_items.filter(category=constants.MODULE_CATEGORYID)
    
    charges = all_types.filter(category=constants.CHARGE_CATEGORYID)
    capital_ships = all_types.filter(group__in=constants.CAPITAL_SHIPS_GROUPID)
    
    for ids in tools.sublists(list(t1_items.values_list('typeID', flat=True)), 200):
        t1_items_group.items.add(*CatalogEntry.objects.filter(typeID__in=ids))
    for ids in tools.sublists(list(t2_items.values_list('typeID', flat=True)), 200):
        t2_items_group.items.add(*CatalogEntry.objects.filter(typeID__in=ids))
    for ids in tools.sublists(list(t3_items.values_list('typeID', flat=True)), 200):
        t3_items_group.items.add(*CatalogEntry.objects.filter(typeID__in=ids))
    
    for ids in tools.sublists(list(t1_ships.values_list('typeID', flat=True)), 200):
        t1_ships_group.items.add(*CatalogEntry.objects.filter(typeID__in=ids))
    for ids in tools.sublists(list(t2_ships.values_list('typeID', flat=True)), 200):
        t2_ships_group.items.add(*CatalogEntry.objects.filter(typeID__in=ids))
    for ids in tools.sublists(list(t3_ships.values_list('typeID', flat=True)), 200):
        t3_ships_group.items.add(*CatalogEntry.objects.filter(typeID__in=ids))
    
    for ids in tools.sublists(list(t1_modules.values_list('typeID', flat=True)), 200):
        t1_modules_group.items.add(*CatalogEntry.objects.filter(typeID__in=ids))
    for ids in tools.sublists(list(t2_modules.values_list('typeID', flat=True)), 200):
        t2_modules_group.items.add(*CatalogEntry.objects.filter(typeID__in=ids))
    for ids in tools.sublists(list(t3_modules.values_list('typeID', flat=True)), 200):
        t3_modules_group.items.add(*CatalogEntry.objects.filter(typeID__in=ids))
    
    for ids in tools.sublists(list(charges.values_list('typeID', flat=True)), 200):
        charges_group.items.add(*CatalogEntry.objects.filter(typeID__in=ids))
    for ids in tools.sublists(list(capital_ships.values_list('typeID', flat=True)), 200):
        capital_ships_group.items.add(*CatalogEntry.objects.filter(typeID__in=ids))
        
    duration = time.time() - start
    logger.info('Initialized item groups (took %.2f sec.)', duration)
    
create_missing_item_groups()

