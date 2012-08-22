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

__date__ = '2011-02-19'
__author__ = 'diabeteman'

from django.template.loader import render_to_string

import ecm
from ecm.apps.common.models import UrlPermission, Motd
from ecm.menu import ECM_MENUS
from ecm.apps.corp.models import Corporation

#------------------------------------------------------------------------------
def corporation_name(request):
    """
    Adds the variable {{ corp_name }} to all the templates.
    """
    try:
        return { "my_corp": Corporation.objects.mine() }
    except Corporation.DoesNotExist:
        return { "my_corp": None }

#------------------------------------------------------------------------------
def version(request):
    """
    Adds the variable {{ ecm_version }} to all the templates.
    """
    return {'ecm_version': ecm.VERSION}

#------------------------------------------------------------------------------
def menu(request):
    """
    Adds the variable {{ user_menu }} to all the templates.

    The menu is composed with items from each ECM app/plugin (see the menu.py files)
    The items are dynamically displayed according to user accesses.
    """
    user_menus = []
    for menu in ECM_MENUS:
        if request.user.is_superuser or UrlPermission.user_has_access(request.user, menu['url']):
            user_menus.append(menu)
    data = {
        'menus': user_menus, 
        'path': str(request.get_full_path())
    }
    return {'user_menu': render_to_string('ecm/menu.html', data), 'request_path': data['path']}

#------------------------------------------------------------------------------
def motd(request):
    
    try:
        motd = Motd.objects.latest()
    except Motd.DoesNotExist:
        motd = None
    can_edit = request.user.is_superuser or UrlPermission.user_has_access(request.user, '/editmotd/')
        
    #{{motd|safe}} to escape html markup
    return {'motd': motd, 'can_edit_motd': can_edit}

    