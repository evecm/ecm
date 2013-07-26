# Copyright (c) 2011 jerome Vacher
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

__date__ = "2012 09 06"
__author__ = "tash"

from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _

from ecm.utils import _json as json
from ecm.apps.eve.models import CelestialObject
from ecm.views.decorators import check_user_access
from ecm.views import extract_datatable_params


@check_user_access()
def list(request):
    limit = 10
    results = ""
    query = request.GET.get('q', None)
    if query:
        instances = CelestialObject.objects.filter(itemName__istartswith=query)[:limit]
        for item in instances:
            results += "%s|%s \n" %(item.pk,item.itemName)
    return HttpResponse(results)
