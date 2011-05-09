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

__date__ = "2011 4 17"
__author__ = "diabeteman"

import json

from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext

from ecm.core import utils
from ecm.view.decorators import user_is_director
from ecm.data.roles.models import Member, CharacterOwnership
from ecm.data.common.models import ColorThreshold
from ecm.view import extract_datatable_params, get_members

#------------------------------------------------------------------------------
@user_is_director()
def player_list(request):
    data = { 
        'colorThresholds' : ColorThreshold.as_json(),
    }
    return render_to_response("auth/player_list.html", data, RequestContext(request))

#------------------------------------------------------------------------------
USER_COLUMNS = ["username", "char_count", "group_count", "date_joined"]
@user_is_director()
def player_list_data(request):
    try:
        extract_datatable_params(request)
    except KeyError:
        return HttpResponseBadRequest()
    
    query = User.objects.filter(is_active=True)
    query = query.exclude(username__in=[settings.CRON_USERNAME, settings.ADMIN_USERNAME])
    query = query.extra(select={
        'group_count': 'SELECT COUNT(*) '
                       'FROM "auth_user_groups" '
                       'WHERE "auth_user_groups"."user_id"="auth_user"."id"',
        'char_count':  'SELECT COUNT(*) '
                       'FROM "roles_characterownership" '
                       'WHERE "roles_characterownership"."owner_id"="auth_user"."id"',
    })
    
    sort_by = USER_COLUMNS[request.column]
    # SQL hack for making a case insensitive sort
    if sort_by == "username":
        sort_col = "%s_nocase" % sort_by
        query = query.extra(select={sort_col : 'LOWER("%s")' % sort_by})
    else:
        sort_col = sort_by
        
    if not request.asc: sort_col = "-" + sort_col
    query = query.extra(order_by=[sort_col])
    
    if request.search:
        total_count = query.count()
        query = query.filter(username__icontains=request.search)
        filtered_count = query.count()
    else:
        total_count = filtered_count = query.count()
    
    query = query[request.first_id:request.last_id]
    player_list = []
    for player in query:
        player_list.append([
            '<a href="/players/%d" class="player">%s</a>' % (player.id, player.username),
            player.char_count,
            player.group_count,
            utils.print_time_min(player.date_joined)
        ])
    
    json_data = {
        "sEcho" : request.sEcho,
        "iTotalRecords" : total_count,
        "iTotalDisplayRecords" : filtered_count,
        "aaData" : player_list
    }
    
    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@user_is_director()
def player_details(request, player_id):
    player = get_object_or_404(User, id=int(player_id))
    
    data = {
        'player': player,
        'colorThresholds' : ColorThreshold.as_json(),
        'directorAccessLvl' : Member.DIRECTOR_ACCESS_LVL
    }
    
    return render_to_response('auth/player_details.html', data, RequestContext(request))

#------------------------------------------------------------------------------
@user_is_director()
def player_details_data(request, player_id):
    try:
        extract_datatable_params(request)
    except KeyError:
        return HttpResponseBadRequest()

    player = get_object_or_404(User, id=int(player_id))
    owned = CharacterOwnership.objects.filter(owner=player)
    
    total_members,\
    filtered_members,\
    members = get_members(query=Member.objects.filter(ownership__in=owned),
                          first_id=request.first_id, 
                          last_id=request.last_id,
                          search_str=request.search,
                          sort_by=request.column, 
                          asc=request.asc)
    json_data = {
        "sEcho" : request.sEcho,
        "iTotalRecords" : total_members,
        "iTotalDisplayRecords" : filtered_members,
        "aaData" : members
    }
    
    return HttpResponse(json.dumps(json_data))
    