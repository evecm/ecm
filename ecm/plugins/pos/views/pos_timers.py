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

from django.shortcuts import render_to_response
from django.template.context import RequestContext

from ecm.plugins.pos.models import Timer 
from ecm.apps.eve.models import Type
from ecm.views.decorators import check_user_access

@check_user_access()
def timers(request):
    timers = Timer.objects.all()
    # Build result list for formatted/labeled data
    timer_list = []
    for timer in timers:
        time_remaining = create_time_remaining(timer.timer)
        t = {
                'location': timer.location,
                'structure': timer.structure_label(),
                'cycle': timer.cycle_label(),
                'location_id': timer.location_id,
                'moon_id': timer.moon_id,
                'owner': timer.owner_id,
                'friendly': timer.friendly,
                'timer': timer.timer,
                'notes': timer.notes,
                'time_remaining': time_remaining,
                'class': create_timer_style(timer.timer)
         }
        timer_list.append(t)

    data = {
           'timers' : timer_list 
           }
    return render_to_response("ecm/pos/pos_timers.html", data, RequestContext(request))

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
    Background color ranges from #000000 to #F80000.
    !!!TODO: Make threshold configurable in POS settings.
    """
    delta = delta_seconds_from_now(date)
    threshold_step = (threshold_alert * 60) / 32
    alert_map = []
    for x in range(0, 255, 8):
        alert_map.append(triplet((x,0,0)))
    if delta <= 0:
        return 'backgroud-color: #383838; color: white;'
    if delta / 60 > 0:
        if delta / 60 < threshold_alert * 60:
            index = 32 - ((delta / 60) / threshold_step) - 1
        else:
            index = 0
        return 'background-color: #%s; color: white; font-weight:bold;' % alert_map[index]
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
