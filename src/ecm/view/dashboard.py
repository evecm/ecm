# The MIT License - EVE Corporation Management
# 
# Copyright (c) 2010 Robin Jarry
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from ecm.core import evedb
from ecm.core.parsers import assetsconstants

__date__ = "2010-02-03"
__author__ = "diabeteman"

import json

from django.shortcuts import render_to_response
from django.template.context import RequestContext

from ecm.data.roles.models import Member, CharacterOwnership
from ecm.data.common.models import ColorThreshold, UserAPIKey
from ecm.view.decorators import user_is_director

#------------------------------------------------------------------------------
@user_is_director()
def dashboard(request):
    data = {
        'unassociatedCharacters' : Member.objects.filter(corped=True, ownership=None).count(),
        'playerCount' : CharacterOwnership.objects.values("owner").distinct().count(),
        'memberCount' : Member.objects.filter(corped=True).count(),
        'accountsByPlayer' : avg_accounts_by_player(),
        'chraractersByPlayer' : avg_chraracters_by_player(),
        'positions' : positions_of_members(),
        'distribution' : access_lvl_distribution(),
        'directorAccessLvl' : Member.DIRECTOR_ACCESS_LVL 
    }
    
    return render_to_response("common/dashboard.html", data, context_instance=RequestContext(request))

#------------------------------------------------------------------------------
def avg_chraracters_by_player():
    players = CharacterOwnership.objects.values("owner").distinct().count()
    characters = float(CharacterOwnership.objects.all().count())
    return characters / players

#------------------------------------------------------------------------------
def avg_accounts_by_player():
    players = CharacterOwnership.objects.values("owner").distinct().count()
    accounts = float(UserAPIKey.objects.all().count())
    return accounts / players

#------------------------------------------------------------------------------
def positions_of_members():
    positions = {"hisec" : 0, "lowsec" : 0, "nullsec" : 0}
    for m in Member.objects.filter(corped=True):
        solarSystemID = m.locationID
        if solarSystemID > assetsconstants.STATIONS_IDS:
            solarSystemID = evedb.getSolarSystemID(m.locationID)
        security = evedb.resolveLocationName(solarSystemID)[1]
        if security > 0.5:
            positions["hisec"] += 1
        elif security > 0:
            positions["lowsec"] += 1
        else:
            positions["nullsec"] += 1
    return json.dumps(positions)

#------------------------------------------------------------------------------
def access_lvl_distribution():
    thresholds = ColorThreshold.objects.all().order_by("threshold")
    for th in thresholds: 
        th.members = 0
    members = Member.objects.filter(corped=True).order_by("accessLvl")
    levels = members.values_list("accessLvl", flat=True)
    i = 0
    for level in levels:
        if level > thresholds[i].threshold:
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
