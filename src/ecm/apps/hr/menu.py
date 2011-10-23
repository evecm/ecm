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

__date__ = "2011 10 14"
__author__ = "diabeteman"

ECM_MENUS = [
    {'menu_title': 'Human Resources',   'menu_url': '',     'menu_items': [
        {'item_title': 'Members',   'item_url': 'members/', 'menu_items': [
            {'item_title': 'History',               'item_url': 'members/history/'},
            {'item_title': 'Access Changes',        'item_url': 'members/accesschanges/'},
            {'item_title': 'Unassociated Members',  'item_url': 'members/unassociated/'},
        ]},
        {'item_title': 'Titles',    'item_url': 'titles/',      'menu_items': [
            {'item_title': 'Changes',               'item_url': 'titles/changes/'},
        ]},
        {'item_title': 'Roles',     'item_url': 'roles/',       'menu_items': [
            {'item_title': 'General',               'item_url': 'roles/roles/'}, 
            {'item_title': 'Grantable General',     'item_url': 'roles/grantableRoles/'}, 
            {'item_title': 'At HQ',                 'item_url': 'roles/rolesAtHQ/'}, 
            {'item_title': 'Grantable At HQ',       'item_url': 'roles/grantableRolesAtHQ/'}, 
            {'item_title': 'At Base',               'item_url': 'roles/rolesAtBase/'}, 
            {'item_title': 'Grantable At Base',     'item_url': 'roles/grantableRolesAtBase/'}, 
            {'item_title': 'At Other',              'item_url': 'roles/rolesAtOther/'}, 
            {'item_title': 'Grantable At Other',    'item_url': 'roles/grantableRolesAtOther/'}
        ]},
        {'item_title': 'Players',   'item_url': 'players/',     'menu_items': []},
    ]},
]
