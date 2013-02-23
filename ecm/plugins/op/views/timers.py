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

from datetime import datetime

try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _

from ecm.plugins.op.models import Timer
from ecm.plugins.op.forms import TimerForm
from ecm.apps.eve.models import Type
from ecm.views.decorators import check_user_access
from ecm.views import extract_datatable_params

@check_user_access()
def timers(request):
    # Location  Type    Cycle   Planet  Moon    Owner   Friendly    Date    Notes   Time Remaining
    header = [_('Location'), _('Type'), _('Cycle'), _('Planet'), _('Moon'), _('Owner'), _('Friendly'), _('Date'), _('Notes'), _('Time Remaining')]
    data = {
    #       'timers' : timer_list,
           'header' : header
           }
    return render_to_response("ecm/op/timers.html", data, RequestContext(request))

@check_user_access()
def timers_data(request):
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        params.display_all = REQ.get('display_all', 'days')
    except:
        return HttpResponseBadRequest()
    timers = Timer.objects.all()
    ordering_map = {
        0: 'location',
        1: 'structure',
        2: 'cycle',
        3: 'location_id',
        4: 'moon_id',
        5: 'owner_id',
        6: 'friendly',
        7: 'timer',
        8: 'notes',
        9: 'timer',
        }
    if params.column in ordering_map:
        sort_order = ''
        sort_order += '-' if not params.asc else ''
        sort_order += ordering_map[params.column]
        timers = timers.order_by(sort_order)

    print params.display_all
    if not params.display_all:
        timers =  timers.filter(timers__gte=datetime.utcnow())

    # Build result list for formatted/labeled data
    timer_list = []
    na = '-'
    total_entries = filtered_entries = timers.count()

    for timer in timers:
        t = {
                '0': '<a href="http://evemaps.dotlan.net/system/%s" target="_blank">%s</a>' % (timer.location, timer.location),
                '1': timer.structure_label(),
                '2': timer.cycle_label(),
                '3': timer.location_id if timer.location_id else na,
                '4': timer.moon_id if timer.moon_id else na,
                '5': timer.owner_id if timer.owner_id else na,
                '6': timer.friendly,
                '7': timer.timer.strftime('%Y-%m-%d %H:%M:%S'),
                '8': timer.notes,
                '9': create_time_remaining(timer.timer),
                '10': create_timer_style(timer.timer)
         }
        timer_list.append(t)
        """timer_list.append([timer.location,
                           timer.structure_label(),
                           timer.cycle_label(),
                           timer.location_id if timer.location_id else na,
                           timer.moon_id if timer.moon_id else na,
                           timer.owner_id if timer.owner_id else na,
                           timer.friendly,
                           timer.timer.strftime('%Y-%m-%dT%H:%M:%S'), 
                           timer.notes, create_time_remaining(timer.timer),
                           create_timer_style(timer.timer)])
"""
    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_entries,
        "iTotalDisplayRecords" : filtered_entries,
        "aaData" : timer_list,
    }
    return HttpResponse(json.dumps(json_data))

@check_user_access()
def add_timer(request):
    form = TimerForm(request.POST) 
    if form.is_valid():
        return HttpResponseRedirect('/')
    else:
        form = TimerForm()
    return render_to_response("ecm/op/add_timer.html", {'form' : form,}, RequestContext(request))

def triplet(rgb):
    """
    Utility method that returns #RGB for a given tuple (red, green, blue).
    """
    return format((rgb[0]<<16)|(rgb[1]<<8)|rgb[2], '06x')

def create_timer_style(date, threshold_alert=24):
    """
    Returns a css style wrt. time remaining.
    The background color is created based on the remaining time scaled by threshold_alert.
    A timer that expires in 4 hours has a brighter red then a timer due in 24 hours.
    Background color ranges from #444444 (bg-color of navbar) to #F84444.
    """
    delta = delta_seconds_from_now(date)
    threshold_step = (threshold_alert * 60) / 26
    alert_map = []
    for x in range(44, 255, 8):
        alert_map.append(triplet((x,44,44)))
    if delta <= 0:
        return 'background-color: #242424 !important; color: white;'
    if delta / 60 > 0:
        if delta / 60 < threshold_alert * 60:
            index = 26 - ((delta / 60) / threshold_step)
        else:
            index = 0
        return 'background-color: #%s; color: white;' % alert_map[index]
    return 'timer'

def create_time_remaining(date):
    """
    Returns the remaining time from utcnow in a string "HHh MMm SSs".
    If delta is <= 0 the returned string is "Expired".
    """
    delta_seconds = delta_seconds_from_now(date)
    if delta_seconds <= 0:
        return "Expired"
    hours, remainder = divmod(delta_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '%sh %sm %ss' % (hours, minutes, seconds)

def delta_seconds_from_now(date):
    """
    Note: tzinfo is stripped from date.
    """
    delta = date.replace(tzinfo=None) - datetime.utcnow()
    # timedelta.total_seconds() introduced in python 2.7, so do it by hand for downward compat
    return (delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 10**6) / 10**6
