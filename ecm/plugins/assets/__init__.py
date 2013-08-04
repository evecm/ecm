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


NAME = 'assets'
VERSION = '2.0'

DEPENDS_ON = {
    'ecm' : '2.0',
}

MENUS = [
    {'title': tr_lazy('Assets'),    'url': '',      'items': [
        {'title': tr_lazy('Changes'), 'url': 'changes/', 'items': []},
    ]},
]

TASKS = [
    {
        'function' : 'ecm.plugins.assets.tasks.assets.update',
        'priority' : 0,
        'frequency' : 6,
        'frequency_units' : 60 * 60, # hour
    },
]

URL_PERMISSIONS = [
    r'^/assets/.*$',
]

SETTINGS = {
    'assets_show_exact_volumes': False,
    'assets_ignore_containers_volumes': True,
}
