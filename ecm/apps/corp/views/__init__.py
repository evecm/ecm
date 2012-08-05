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

__date__ = '2012 08 01'
__author__ = 'diabeteman'

import re
try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext as Ctx

from ecm.utils import crypto
from ecm.apps.common import api
from ecm.apps.hr.models.member import Member
from ecm.apps.corp.views import auth
from ecm.apps.corp.models import Corporation


#------------------------------------------------------------------------------
SHOWINFO_PATTERN = re.compile(r'showinfo:13\d\d//(\d+)')
@login_required
def corp(request):
    try:
        corp = Corporation.objects.mine()
        corp.description = SHOWINFO_PATTERN.sub(r'/hr/members/\1/', corp.description)
        corp.memberCount = Member.objects.filter(corped=True).count()
    except Corporation.DoesNotExist:
        corp = Corporation(corporationName='No Corporation info')
    
    return render_to_response('ecm/corp/corp.html', {'corp': corp}, Ctx(request))


#------------------------------------------------------------------------------
def public_info(request):
    
    my_corp = Corporation.objects.mine()
    
    data = {
        'public_key': my_corp.public_key,
        'key_fingerprint': my_corp.key_fingerprint,
        'corp_id': my_corp.corporationID,
        'corp_name': my_corp.corporationName,
        'alliance_id': my_corp.allianceID,
        'alliance_name': my_corp.allianceName,
    }
    
    return HttpResponse(json.dumps(data))

#------------------------------------------------------------------------------
def login(request):
    if request.method == 'POST':
        return auth.post_response(request)
    else:
        return auth.get_challenge(request)

#------------------------------------------------------------------------------
@auth.active_session_required()
def list_available_data(request):
    
    data = crypto.aes_encrypt(request.session[auth.AUTH_SECRET], 'Bonsoir madame la marquise')
    
    return HttpResponse(data)