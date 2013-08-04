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

NAME = 'corp'

MENUS = [ 
    {'title': tr_lazy('Corporation'),    'url': '',      'items': [
        {'title': tr_lazy('Standings'),   'url': 'standings/', 'items': [], },
    ]},
]

TASKS = [
    {
        'function' : 'ecm.apps.corp.tasks.corp.update',
        'priority' : 200,
        'frequency' : 12,
        'frequency_units' : 60 * 60, # hour
    },
    {
        'function' : 'ecm.apps.corp.tasks.standings.update',
        'priority' : 200,
        'frequency' : 24,
        'frequency_units' : 60 * 60, # hour
    },
    {
        'function' : 'ecm.apps.corp.tasks.multicorp.update_all',
        'priority' : 200,
        'frequency' : 24,
        'frequency_units' : 60 * 60, # hour
    },
]

SHARED_DATA = [
    {'url': 'share/details/',   'handler': 'ecm.apps.corp.share.process_details'},
    {'url': 'share/standings/corp/', 'handler': 'ecm.apps.corp.share.process_corp_standings'},
    {'url': 'share/standings/alliance/', 'handler': 'ecm.apps.corp.share.process_alliance_standings'},
]

SETTINGS = {
    'corp_killboard_url': None,
    'standings_visibility': 'none',
}
