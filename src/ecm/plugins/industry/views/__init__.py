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

__date__ = "2011 8 19"
__author__ = "diabeteman"

import logging

from django.db import connections, transaction

from ecm.apps.eve.models import Type, BlueprintReq

from ecm.plugins.industry.models import CatalogEntry, Supply

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
def print_duration(seconds):
    seconds = int(seconds)
    if not seconds > 0:
        return '0 sec.'
    duration = ''
    days = seconds / DAY
    if days > 0:
        duration += '%d day' % days
        if days > 1:
            duration += 's'
    rest = seconds % DAY
    hours = rest / HOUR
    if hours > 0:
        duration += ' %d hour' % hours
        if hours > 1:
            duration += 's'
    rest = rest % HOUR
    minutes = rest / MINUTE
    if minutes > 0:
        duration += ' %d min.' % minutes
    rest = rest % MINUTE
    if rest > 0:
        duration += ' %d sec.' % rest
    return duration.strip()

#------------------------------------------------------------------------------
SQL_MISSING_ITEMS = '''SELECT "typeID", "typeName"
FROM "invTypes"
WHERE "blueprintTypeID" IS NOT NULL
  AND "published" = 1
  AND "metaGroupID" IN (0,2,14)
  AND "marketGroupID" IS NOT NULL
  AND "typeID" NOT IN (2836, 17922, 29266, 17928, 17932, 3532, 32207, 32209);'''
@transaction.commit_on_success
def createMissingCatalogEntries():
    typeIDs = CatalogEntry.objects.values_list('typeID', flat=True)
    cursor = connections['eve'].cursor()
    cursor.execute(SQL_MISSING_ITEMS)
    created = 0
    for typeID, typeName in cursor:
        if typeID not in typeIDs:
            CatalogEntry.objects.create(typeID=typeID, typeName=typeName, is_available=False)
            created += 1
    logger.info('added %d missing catalog entries', created)
createMissingCatalogEntries()
#------------------------------------------------------------------------------
SQL_MISSING_SUPPLIES = '''SELECT DISTINCT "requiredTypeID"
FROM "ramBlueprintReqs" AS r JOIN "invTypes" AS i ON r."requiredTypeID" = i."typeID"
WHERE i."blueprintTypeID" IS NULL
AND i."published" = 1
AND r."damagePerJob" > 0.0;'''
@transaction.commit_on_success
def createMissingSupplies():
    typeIDs = Supply.objects.values_list('typeID', flat=True)
    cursor = connections['eve'].cursor()
    cursor.execute(SQL_MISSING_SUPPLIES)
    created = 0
    for typeID, in cursor:
        if typeID not in typeIDs:
            Supply.objects.create(typeID=typeID)
            created += 1
    logger.info('added %d missing supplies', created)
createMissingSupplies()

#------------------------------------------------------------------------------
@transaction.commit_on_success
def createMissingCatalogEntries_new():
    entries = Type.objects.filter(blueprint__isnull = False,
                                  published = 1,
                                  metaGroupID__in = [0,2,14],
                                  market_group__isnull = False,
                                  ).exclude(typeID__in=[2836, 17922, 29266, 17928, 17932, 3532, 32207, 32209])
    typeIDs = CatalogEntry.objects.values_list('typeID', flat=True)
    created = 0
    for typeID, typeName in [(i.typeID, i.typeName) for i in entries]:
        if typeID not in typeIDs:
            CatalogEntry.objects.create(typeID=typeID, typeName=typeName, is_available=False)
            created += 1
    logger.info('added %d missing catalog entries', created)
#createMissingCatalogEntries_new()

#------------------------------------------------------------------------------
@transaction.commit_on_success
def createMissingSupplies_new():
    supplies= BlueprintReq.objects.filter(required_type__blueprint__isnull=True, 
                                          required_type__published=1, 
                                          damagePerJob__gt=0.0).values_list('requiredTypeID', 
                                                                            flat=True).distinct()
    typeIDs = Supply.objects.values_list('typeID', flat=True)
    created = 0
    for typeID in [x.typeID for x in supplies]:
        if typeID not in typeIDs:
            Supply.objects.create(typeID=typeID)
            created += 1
    logger.info('added %d missing supplies', created)
#createMissingSupplies_new()