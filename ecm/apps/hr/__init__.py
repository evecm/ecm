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

from django.utils.translation import ugettext_lazy as tr_lazy

NAME = 'hr'

MENUS = [
    {'title': tr_lazy('Human Resources'),   'url': '',     'items': [
        {'title': tr_lazy('Members'),   'url': 'members/', 'items': [
            {'title': tr_lazy('History'),               'url': 'members/history/'},
            {'title': tr_lazy('Access Changes'),        'url': 'members/accesschanges/'},
            {'title': tr_lazy('Unassociated Members'),  'url': 'members/unassociated/'},
            {'title': tr_lazy('Skills'),                'url': 'members/skills/'},
            {'title': tr_lazy('Cyno Alts'),             'url': 'members/cyno_alts/'},
        ]},
        {'title': tr_lazy('Titles'),    'url': 'titles/',      'items': [
            {'title': tr_lazy('Changes'),               'url': 'titles/changes/'},
        ]},
        {'title': tr_lazy('Roles'),     'url': 'roles/',       'items': []},
        {'title': tr_lazy('Players'),   'url': 'players/',     'items': []},
    ]},
]

TASKS = [
    {
        'function': 'ecm.apps.hr.tasks.titles.update',
        'priority': 50,
        'frequency': 6,
        'frequency_units': 60 * 60, # hour
    }, {
        'function': 'ecm.apps.hr.tasks.members.update',
        'priority': 20,
        'frequency': 2,
        'frequency_units': 60 * 60, # hour
    }, {
        'function': 'ecm.apps.hr.tasks.users.update_all_character_associations',
        'priority': 5,
        'frequency': 1,
        'frequency_units': 60 * 60 * 24, # day
    }, {
        'function': 'ecm.apps.hr.tasks.users.update_all_users_accesses',
        'priority': 1,
        'frequency': 2,
        'frequency_units': 60 * 60, # hour
    },
]

URL_PERMISSIONS = [
    r'^/hr/$',
    r'^/hr/members/.*$',
    r'^/hr/roles/.*$',
    r'^/hr/titles/.*$',
    r'^/hr/players/.*$',
    r'^/hr/members/cyno_alts/.*$',
]

SHARED_DATA = [
    {'url': 'share/members/', 'handler': 'ecm.apps.hr.share.process_members'},
    {'url': 'share/players/', 'handler': 'ecm.apps.hr.share.process_players'},
    {'url': 'share/skills/',  'handler': 'ecm.apps.hr.share.process_skills'},
]

SETTINGS = {
    'hr_corp_members_group_name': 'Members',
    'hr_directors_group_name': 'Directors',
    'hr_recruiters_group_name': 'Recruiters',
    'hr_allies_plus_5_group_name': 'Allies +5',
    'hr_allies_plus_10_group_name': 'Allies +10',
}

