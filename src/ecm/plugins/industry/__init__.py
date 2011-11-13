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

__date__ = "2011 8 17"
__author__ = "diabeteman"


NAME = 'industry'

DEPENDS_ON = {
    'ecm' : (2,),
}

MENUS = [
    {'menu_title': 'Industry',    'menu_url': '',      'menu_items': [
        {'item_title': 'Orders', 'item_url': 'orders/', 'menu_items': []},
        {'item_title': 'Catalog', 'item_url': 'catalog/', 'menu_items': []},
        {'item_title': 'Supply Prices', 'item_url': 'prices/', 'menu_items': []},
    ]},
]

TASKS = [
    {
        'function' : 'ecm.plugins.industry.tasks.industry.update_supply_prices',
        'priority' : 0,
        'frequency' : 24,
        'frequency_units' : 3600, # hour
    },
]

URL_PERMISSIONS = [
    r'^/industry.*$',
]
