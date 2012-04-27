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

__date__ = "2012-04-26"
__author__ = "Ajurna"



from django.shortcuts import render_to_response
from django.template.context import RequestContext

from ecm.apps.corp.models import Standings
from ecm.apps.common.models import Setting

#------------------------------------------------------------------------------
def standings(request):
    allaince_standings = Standings.objects.filter(is_corp_contact=False)
    allaince_standings = allaince_standings.order_by('-standing', 'contactName')
    corp_standings = Standings.objects.filter(is_corp_contact=True)
    corp_standings = corp_standings.order_by('-standing', 'contactName')
    data = {}
    try: 
        standings_public = Setting.objects.get(name='standings_public')
    except Setting.DoesNotExist:
        Setting.objects.create('standings_public', 'none')
        standings_public = Setting.objects.get('standings_public')
    if request.user.is_superuser:
        if request.method == 'POST':
            standings_public.value = request.POST['standings_public']
            standings_public.save()
    data['standings_public'] = standings_public.value
    data['allaince_standings'] = allaince_standings
    data['corp_standings'] = corp_standings
    
    return render_to_response("common/standings.html",
                              data,
                              RequestContext(request),
                              )
