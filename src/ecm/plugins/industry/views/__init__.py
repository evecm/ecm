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

__date__ = "2011 8 19"
__author__ = "diabeteman"


try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required

from ecm.plugins.industry.models import CatalogEntry

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
  AND "typeID" NOT IN %s;'''
CatalogEntry.objects.values_list('typeID', flat=True)




