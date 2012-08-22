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


__date__ = "2012 08 09"
__author__ = "Ajurna"


from django.shortcuts import render_to_response
from django.template.context import RequestContext as Ctx


from ecm.views.decorators import check_user_access
from ecm.apps.alerts.alerts import ALERT_SIGNAL

@check_user_access()
def alert_list(request):
    return render_to_response('ecm/alerts/list.html', Ctx(request))


def task():
    print "task running"
    data = {}
    data['message'] = 'complete'
    ALERT_SIGNAL.send(sender = None, 
                      data = data,
                      task = 'ecm.apps.alerts.views.task',
                      )

