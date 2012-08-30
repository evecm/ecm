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

__date__ = "2012 08 01"
__author__ = "diabeteman"

from django.db.models.aggregates import Count
from django.contrib.auth.models import User

from ecm.apps.corp.models import Corporation
from ecm.apps.corp.views.auth import valid_session_required, encrypted_response

#------------------------------------------------------------------------------
@valid_session_required
def members(request):
    my_corp = Corporation.objects.mine()
    data = []
    for member in my_corp.members.all():
        data.append(member.get_shared_info())
    return encrypted_response(request, data, compress=True)

#------------------------------------------------------------------------------
@valid_session_required
def players(request):
    my_corp = Corporation.objects.mine()
    
    users = User.objects.filter(is_active=True).select_related(depth=1)
    users = users.annotate(char_count=Count("characters"))
    players = users.filter(char_count__gt=0)
    
    data = []
    for player in players:
        
        if not player.characters.filter(corp=my_corp):
            continue
        
        data.append({
            'username': player.username,
            'characters': [ c.characterID for c in player.characters.filter(corp=my_corp) ],
        })
    
    return encrypted_response(request, data, compress=True)

#------------------------------------------------------------------------------
@valid_session_required
def skills(request):
    my_corp = Corporation.objects.mine()
    
    data = []
    for member in my_corp.members.all():
        data.append({
            'characterID': member.characterID,
            'skills': list(member.skills.values('eve_type_id', 'level')),
        })
    
    return encrypted_response(request, data, compress=True)
