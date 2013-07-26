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


from django.db.models import Q
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect,\
    Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _

from ecm.utils import _json as json
from ecm.plugins.op.models import Timer
from ecm.plugins.op.forms import TimerForm
from ecm.views.decorators import check_user_access
from ecm.views import extract_datatable_params

# Table header
header = [  
    '',
    _('Solarsystem'),
    _('Type'),
    _('Cycle'),
    _('Celestial'),
    _('Owner'),
    _('Friendly'),
    _('Date'),
    _('Notes'),
    _('Time Remaining')
]

# Table ordering map
ordering_map = {
    1: 'location',
    2: 'structure',
    3: 'cycle',
    4: 'location',
    5: 'owner_id',
    6: 'friendly',
    7: 'timer',
    8: 'notes',
    9: 'timer',
}
# 'Not available' icon
na = '<i class="icon-minus"></i>'

# DOTLAN system linkt format
link_dotlan = '<a href="http://evemaps.dotlan.net/system/%s" target="_blank">%s</a>'

# Buttons format
btn_edit = '<a class="btn btn-mini" href="edit/%s/"><i class="icon-edit"></i></a>'
btn_remove = '<a class="btn btn-mini" href="remove/%s/"><i class="icon-remove-sign"></i></a>'

@check_user_access()
def timers(request):
    data = {'header' : header}
    return render_to_response("ecm/op/timers.html", data, RequestContext(request))

@check_user_access()
def timers_data(request):
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        params.display_all = REQ.get('display_all', 'days')
    except:
        return HttpResponseBadRequest()
    timers = Timer.objects.filter(Q(timer__gte=datetime.now(utc)))
    # Set the sort order
    if params.column in ordering_map:
        sort_order = ''
        sort_order += '-' if not params.asc else ''
        sort_order += ordering_map[params.column]
        timers = timers.order_by(sort_order)

    if not params.display_all:
        timers =  timers.filter(timers__gte=datetime.utcnow())

    # Build result list for formatted/labeled data
    timer_list = []
    total_entries = filtered_entries = timers.count()
    for timer in timers:
        t = {
                '0': btn_edit % timer.id + btn_remove % timer.id,
                '1': link_dotlan % (timer.location_label(), timer.location_label()),
                '2': timer.structure_label(),
                '3': timer.cycle_label(),
                '4': link_dotlan % (timer.location_dotlan(), timer.location) if timer.location else na,
                '5': timer.owner if timer.owner else na,
                '6': '<i class="icon-ok"></i>' if timer.friendly else na, 
                '7': timer.timer.strftime('%Y-%m-%d %H:%M:%S'),
                '8': timer.notes,
                '9': create_time_remaining(timer.timer),
         }
        timer_list.append(t)
    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_entries,
        "iTotalDisplayRecords" : filtered_entries,
        "aaData" : timer_list,
    }
    return HttpResponse(json.dumps(json_data))

@check_user_access()
def add_timer(request):
    if request.method == 'POST':
        form = TimerForm(request.POST) 
        if form.is_valid():
            form.save()
            # Redirect to timer overview page
            return HttpResponseRedirect('/op/timers')
    else:
        form = TimerForm()
    # Create the form context
    context = RequestContext(request, {'form': form,})
    return render_to_response("ecm/op/add_timer.html", context)

@check_user_access()
def edit_timer(request, timer_id):
    """
    Serves URL /op/timers/edit/<id>/
    Edit an existing timer.
    """
    if request.method == 'POST':
        form =  TimerForm(request.POST)
        if form.is_valid():
            # Fetch the timer object for given id
            timer = Timer.objects.get(pk=timer_id) 
            # populate form with post data for given instance
            form = TimerForm(request.POST, instance=timer)
            # Save changes to DB
            form.save()
            # Redirect to timer overview page
            return HttpResponseRedirect('/op/timers')
    else:
        # Timer form with populated data
        try:
            # Get the timer object by id
            timer = get_object_or_404(Timer, id=int(timer_id))
            # Create the form
            form = TimerForm(instance=timer)
            # Create the form context
            context = RequestContext(request, {'form': form, 'id': timer_id})
            return render_to_response("ecm/op/edit_timer.html", context)
        except ValueError:
            raise Http404()


@check_user_access()
def remove_timer(request, timer_id):
    try:
        # Get the timer object by id
        timer = get_object_or_404(Timer, id=int(timer_id))
        timer.delete()
    except ValueError:
        raise Http404()
    return HttpResponseRedirect('/op/timers')

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
