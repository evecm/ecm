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

__date__ = '2012 04 01'
__author__ = 'tash'



try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

from django.shortcuts import render_to_response
from django.template.context import RequestContext as Ctx
from django.template.defaultfilters import pluralize
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from django.db import connection
from django.db.models.query_utils import Q

from ecm.views.decorators import check_user_access
from ecm.apps.eve.models import CelestialObject, Type
from ecm.apps.eve import constants
from ecm.core import utils
from ecm.plugins.assets.models import Asset
from ecm.apps.corp.models import Hangar
from ecm.views import getScanDate
from ecm.apps.common.models import Setting
from ecm.plugins.assets.views import extract_divisions, HTML_ITEM_SPAN


#------------------------------------------------------------------------------
@check_user_access()
def contracts(request):
    return render_to_response('contracts_no_data.html', Ctx(request))

