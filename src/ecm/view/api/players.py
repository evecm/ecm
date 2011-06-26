# Copyright (c) 2010-2011 Robin Jarry
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

__date__ = "2011 6 26"
__author__ = "diabeteman"

import json

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models.aggregates import Count
from django.contrib.auth.models import User
from django.conf import settings

from ecm.view.decorators import basic_auth_required
from ecm.data.common.models import ExternalApplication

#------------------------------------------------------------------------------
@basic_auth_required(username=settings.CRON_USERNAME)
def players(request):
    query = User.objects.filter(is_active=True)
    query = query.annotate(char_count=Count("characters"))
    query = query.filter(char_count__gt=0)
    query = query.exclude(username__in=[settings.CRON_USERNAME, settings.ADMIN_USERNAME])
    members = []
    for player in query:
        characters = list(player.characters.values_list('character__name', flat=True))
        characters.sort(key=lambda name: name.lower())
        bindings = [{
            'application': b.external_app.name,
            'external_name': b.external_name,
            'external_id': b.external_id
        } for b in player.bindings.all()]
        members.append({
            'id': player.id,
            'username': player.username, 
            'groups': list(player.groups.values_list('id', flat=True)),
            'characters': characters,
            'bindings': bindings
        })
    return HttpResponse(json.dumps(members))

#------------------------------------------------------------------------------
@basic_auth_required(username=settings.CRON_USERNAME)
def binding(request, name):
    query = get_object_or_404(ExternalApplication, name=name).bindings
    query = query.annotate(char_count=Count("user__characters"))
    query = query.filter(user__is_active=True)
    query = query.filter(char_count__gt=0)
    members = []
    for binding in query:
        characters = list(binding.user.characters.values_list('character__name', flat=True))
        characters.sort(key=lambda name: name.lower())
        members.append({
            'external_id': binding.external_id,
            'external_name': binding.external_name, 
            'groups': list(binding.user.groups.values_list('id', flat=True)),
            'characters': characters,
        })
    return HttpResponse(json.dumps(members))

