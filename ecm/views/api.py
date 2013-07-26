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

__date__ = "2011 6 26"
__author__ = "diabeteman"


from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models.aggregates import Count
from django.contrib.auth.models import User

from ecm.utils import _json as json
from ecm.views.decorators import basic_auth_required
from ecm.apps.common.models import ExternalApplication, GroupBinding, UserBinding, Setting

#------------------------------------------------------------------------------
@basic_auth_required(username=Setting.get('common_cron_username'))
def players(request):
    query = User.objects.select_related(depth=3).filter(is_active=True)
    query = query.annotate(char_count=Count("characters"))
    query = query.filter(char_count__gt=0)
    query = query.exclude(username__in=[Setting.get('common_cron_username'), 
                                        Setting.get('common_admin_username')])
    members = []
    for player in query:
        characters = list(player.characters.values('name',
                                                   'characterID'))
        characters.sort(key=lambda x: x['name'].lower())
        bindings = list(player.bindings.values('external_app__name',
                                               'external_name',
                                               'external_id'))
        members.append({
            'id': player.id,
            'username': player.username,
            'characters': characters,
            'bindings': bindings
        })
    return HttpResponse(json.dumps(members))

#------------------------------------------------------------------------------
@basic_auth_required(username=Setting.get('common_cron_username'))
def user_bindings(request, app_name):
    app = get_object_or_404(ExternalApplication, name=app_name)
    query = app.user_bindings.select_related(depth=3)
    query = query.annotate(char_count=Count("user__characters"))
    query = query.filter(user__is_active=True)
    query = query.filter(char_count__gt=0)

    group_bindings = {}
    for gb in GroupBinding.objects.filter(external_app=app):
        group_bindings[gb.group] = gb

    members = []
    for binding in query:
        characters = list(binding.user.characters.values('name',
                                                         'characterID'))
        characters.sort(key=lambda x: x['name'].lower())

        groups = set()
        for g in binding.user.groups.all():
            try: groups.add(group_bindings[g].external_id)
            except KeyError: pass

        members.append({
            'external_id': binding.external_id,
            'external_name': binding.external_name,
            'groups': list(groups),
            'characters': characters,
        })
    return HttpResponse(json.dumps(members))

#------------------------------------------------------------------------------
@basic_auth_required(username=Setting.get('common_cron_username'))
def group_bindings(request, app_name):
    app = get_object_or_404(ExternalApplication, name=app_name)
    groups = {}

    users = UserBinding.objects.filter(external_app=app).select_related(depth=1)

    for gb in app.group_bindings.select_related(depth=3):
        group_users = users.filter(user__in=gb.group.user_set.all())
        external_ids = group_users.values_list('external_id', flat=True)
        try:
            groups[gb.external_id].update(set(external_ids))
        except KeyError:
            groups[gb.external_id] = set(external_ids)
    json_data = []
    for group_id, members in groups.items():
        json_data.append({'group' : group_id, 'members' : list(members)})

    return HttpResponse(json.dumps(json_data))
