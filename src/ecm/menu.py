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

__date__ = "2011 10 16"
__author__ = "diabeteman"

from ecm import plugins
from ecm.data.roles.models import RoleType

role_types = []
for rt in RoleType.objects.all().order_by('id'):
    role_types.append({'item_title': rt.dispName, 'item_url': '/roles/%s/' % rt.typeName})

ECM_MENUS = [
    {'menu_title': 'Home',      'menu_url': '/',            'menu_items': []},
    {'menu_title': 'Human Resources',   'menu_url': '/dashboard/',     'menu_items': [
        {'item_title': 'Members', 'item_url': '/members/', 'menu_items': [
             {'item_title': 'History', 'item_url': '/members/history/'},
             {'item_title': 'Access Changes', 'item_url': '/members/accesschanges/'},
             {'item_title': 'Unassociated Members', 'item_url': '/members/unassociated/'},
        ]},
        {'item_title': 'Titles',    'item_url': '/titles/',      'menu_items': [
             {'item_title': 'Changes', 'item_url': '/titles/changes/'},
        ]},
        {'item_title': 'Roles',     'item_url': '/roles/',  'menu_items': role_types},
        {'item_title': 'Players',   'item_url': '/players/',     'menu_items': []},
    ]},
]

for plugin in plugins.LIST:
    ECM_MENUS += plugin.menu

ECM_MENUS += [
    {'menu_title': 'Scheduled Tasks',   'menu_url': '/tasks/',     'menu_items': []},
]
