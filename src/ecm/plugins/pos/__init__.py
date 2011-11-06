# Copyright (c) 2011 jerome Vacher
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


NAME = 'pos'

DEPENDS_ON = {
    'common' : (2,),
    'corp' : (2,),
    'hr' : (2,),
    'scheduler' : (2,),
}

MENUS = [
     {'menu_title': 'POS',    'menu_url': '',      'menu_items': []},
]

TASKS = [
    {
        'function' : 'ecm.plugins.pos.tasks.pos.update',
        'priority' : 100,
        'frequency' : 6,
        'frequency_units' : 3600, # hour
    },
]

URL_PERMISSIONS = [
    r'^/pos.*$',
]
