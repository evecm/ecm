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
from django.db import transaction

__date__ = "2011 8 19"
__author__ = "diabeteman"


try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json
import logging

from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.db import connections

from ecm.plugins.industry.models import CatalogEntry

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@login_required
def search_item(request):
    querystring = request.GET.get('q', None)
    try:
        limit = int(request.GET.get('limit', "10"))
    except ValueError:
        limit = 10
    if querystring is not None:
        query = CatalogEntry.objects.filter(typeName__icontains=querystring).order_by('typeName')
        matches = query[:limit].values_list('typeName', flat=True)
        return HttpResponse( '\n'.join(matches) )
    else:
        return HttpResponseBadRequest()

#------------------------------------------------------------------------------
@login_required
def get_item_id(request):
    querystring = request.GET.get('q', None)
    if querystring is not None:
        query = CatalogEntry.objects.filter(typeName__iexact=querystring)
        if query.exists():
            item = query[0]
            return HttpResponse( json.dumps( [item.typeID, item.typeName] ) )
        else:
            return HttpResponseNotFound()
    else:
        return HttpResponseBadRequest()

#------------------------------------------------------------------------------
SQL_MISSING_ITEMS = '''SELECT "typeID", "typeName", "marketGroupID"
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
    for typeID, typeName, marketGroupID in cursor:
        if typeID not in typeIDs:
            CatalogEntry.objects.create(typeID=typeID, typeName=typeName, 
                                        marketGroupID=marketGroupID, isAvailable=False)
            created += 1
    logger.info('added %d missing catalog entries', created)
createMissingCatalogEntries()




