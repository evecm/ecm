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

__date__ = "2010-05-16"
__author__ = "diabeteman"


import re

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext

from ecm.apps.hr.models import Member
from ecm.apps.corp.models import Corp

#------------------------------------------------------------------------------
SHOWINFO_PATTERN = re.compile(r"showinfo:13\d\d//(\d+)", re.IGNORECASE + re.DOTALL)
@login_required
def corp(request):
    try:
        corp = Corp.objects.get(id=1)
        corp.description = SHOWINFO_PATTERN.subn(r"/hr/members/\1/", corp.description)[0]
        corp.memberCount = Member.objects.filter(corped=True).count()
    except Corp.DoesNotExist:
        corp = Corp(corporationName="No Corporation info")

    data = { 'corp' : corp }

    return render_to_response("common/corp.html", data, RequestContext(request))





