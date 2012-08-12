# Copyright (c) 2011 Robin Jarry
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

__date__ = "2012-04-26"
__author__ = "Ajurna"



from django.http import Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from ecm.apps.corp.models import Corporation, Standing
from ecm.apps.common.models import Setting

#------------------------------------------------------------------------------
def standings(request):
    corp_id = request.GET.get('corp')
    if corp_id is not None:
        try:
            corp = Corporation.objects.get(corporationID=int(corp_id))
        except (ValueError, Corporation.DoesNotExist):
            raise Http404()
    else:
        corp = Corporation.objects.mine()  
    
    standings = Standing.objects.filter(corp=corp)
    
    alliance_standings = standings.filter(is_corp_contact=False)
    alliance_standings = alliance_standings.order_by('-value', 'contactName')
    corp_standings = standings.filter(is_corp_contact=True)
    corp_standings = corp_standings.order_by('-value', 'contactName')
    
    if request.user.is_superuser:
        if request.method == 'POST':
            visibility = request.POST.get('standings_visibility')
            if visibility:
                Setting.objects.filter(name='standings_visibility').update(value=repr(visibility))

    data = {
        'standings_visibility': Setting.get('standings_visibility'),
        'alliance_standings': alliance_standings,
        'corp_standings': corp_standings,
    }
    
    return render_to_response("ecm/corp/standings.html",
                              data,
                              RequestContext(request),
                              )
