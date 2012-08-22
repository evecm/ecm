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
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext as Ctx

from ecm.apps.corp.models import Corporation


#------------------------------------------------------------------------------
SHOWINFO_PATTERN = re.compile(r'showinfo:13\d\d//(\d+)')
@login_required
def corp(request):
    try:
        corp = Corporation.objects.mine()
        corp.description = SHOWINFO_PATTERN.sub(r'/hr/members/\1/', corp.description)
        corp.memberCount = corp.members.all().count()
    except Corporation.DoesNotExist:
        corp = Corporation(corporationName='No Corporation info')
    
    return render_to_response('ecm/corp/corp.html', {'corp': corp}, Ctx(request))

