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

__date__ = "2010-02-03"
__author__ = "diabeteman"


from datetime import timedelta

from django.db.models.aggregates import Avg
from django.shortcuts import render_to_response
from django.template.context import RequestContext as Ctx
from django.utils import timezone

from ecm.utils import _json as json
from ecm.apps.eve.models import CelestialObject
from ecm.apps.eve import constants
from ecm.apps.corp.models import Corporation
from ecm.views.decorators import check_user_access
from ecm.apps.hr.models import Member
from ecm.apps.hr.models.member import MemberSession
from ecm.apps.common.models import ColorThreshold, UserAPIKey


#------------------------------------------------------------------------------
@check_user_access()
def dashboard(request):
    
    dailyplaytimes = []
    online_member_count = []
    now = timezone.now()
    
    for day in range(30):
        start = now - timedelta(day+1)
        end = now - timedelta(day)
        
        if average_playtime(start,end)['len'] == None:
            time = 0.0
        else:
            time = round((average_playtime(start,end)['len']/3600),2)
        date = start.strftime("%a %b %d")
        online  = members_online(start, end)
        dataset = {'date' : date, 'time' : time} 
        dailyplaytimes.append(dataset)
        dataset = {'date' : date, 'online' : online}
        online_member_count.append(dataset)
    
    corp_id = request.GET.get('corp')
    if corp_id is not None:
        try:
            corp = Corporation.objects.get(corporationID=int(corp_id))
        except (ValueError, Corporation.DoesNotExist):
            corp = None
    else:
        corp = Corporation.objects.mine() 
    
    if corp is not None:
        members = corp.members.all()
    else:
        members = Member.objects.filter(corp__isnull=False)
    
    data = {
        'unassociatedCharacters' : members.filter(owner=None).count(),
        'playerCount' : members.exclude(owner=None).values("owner").distinct().count(),
        'memberCount' : members.count(),
        'accountsByPlayer' : avg_accounts_by_player(corp),
        'chraractersByPlayer' : avg_chraracters_by_player(corp),
        'positions' : positions_of_members(corp),
        'distribution' : access_lvl_distribution(corp),
        'directorAccessLvl' : Member.DIRECTOR_ACCESS_LVL,
        'dailyplaytimes' : dailyplaytimes,
        'online_member_count' : online_member_count,
    }
    
    return render_to_response("ecm/hr/dashboard.html", data, Ctx(request))

#------------------------------------------------------------------------------
def avg_chraracters_by_player(corp=None):
    
    if corp is None:
        members = Member.objects.exclude(owner=None)
    else:
        members = corp.members.exclude(owner=None)
    
    players = members.values("owner").distinct().count()
    characters = float(members.count())
    if players:
        return characters / players
    else:
        return 0.0

#------------------------------------------------------------------------------
def avg_accounts_by_player(corp=None):
    
    if corp is None:
        members = Member.objects.exclude(owner=None)
    else:
        members = corp.members.exclude(owner=None)
    
    players = members.values("owner").distinct().count()
    accounts = float(UserAPIKey.objects.all().count())
    if players:
        return accounts / players
    else:
        return 0.0

#------------------------------------------------------------------------------
def positions_of_members(corp=None):
    
    if corp is None:
        members = Member.objects.all()
    else:
        members = corp.members.all()
    
    positions = {"hisec" : 0, "lowsec" : 0, "nullsec" : 0}
    for m in members:
        solarSystemID = m.locationID
        if solarSystemID > constants.STATIONS_IDS:
            try:
                solarSystemID = CelestialObject.objects.get(itemID = m.locationID).solarSystemID
            except CelestialObject.DoesNotExist:
                solarSystemID = 0
        
        if solarSystemID > 0:
            try:
                security = CelestialObject.objects.get(itemID = solarSystemID).security
            except CelestialObject.DoesNotExist:
                security = 0
        else:
            security = 0

        if security > 0.45:
            positions["hisec"] += 1
        elif security > 0:
            positions["lowsec"] += 1
        else:
            positions["nullsec"] += 1
    return json.dumps(positions)

#------------------------------------------------------------------------------
def access_lvl_distribution(corp=None):
    
    if corp is None:
        members = Member.objects.all()
    else:
        members = corp.members.all()
    
    thresholds = ColorThreshold.objects.all().order_by("threshold")
    for th in thresholds: 
        th.members = 0
    members = members.order_by("accessLvl")
    levels = members.values_list("accessLvl", flat=True)
    i = 0
    for level in levels:
        while level > thresholds[i].threshold:
            i += 1
        thresholds[i].members += 1
    
    distribution_json = []
    
    for th in thresholds:
        distribution_json.append({
            "threshold" : th.threshold,
            "members" : th.members,
            "color" : th.color
        })
    
    return json.dumps(distribution_json)

#------------------------------------------------------------------------------
def average_playtime(start_date, end_date):
    return _get_sessions(start_date, end_date).aggregate(len=Avg('session_seconds'))

def members_online(start_date, end_date):
    return _get_sessions(start_date, end_date).values('character_id').distinct().count()

def _get_sessions(start_date, end_date):
    return MemberSession.objects.filter(session_begin__range=(start_date, end_date))