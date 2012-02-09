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

__date__ = "2011 8 17"
__author__ = "diabeteman"


NAME = 'industry'
VERSION = '1.0'

DEPENDS_ON = {
    'ecm' : '2.0',
}

MENUS = [
    {'title': 'Industry',    'url': '',      'items': [
        {'title': 'Orders', 'url': 'orders/', 'items': []},
        {'title': 'Catalog', 'url': 'catalog/items/', 'items': [
            {'title': 'Blueprints',    'url': 'catalog/blueprints/'},
            {'title': 'Supplies',      'url': 'catalog/supplies/'},
        ]},
    ]},
]

TASKS = [
    {
        'function' : 'ecm.plugins.industry.tasks.industry.update_supply_prices',
        'priority' : 0,
        'frequency' : 24,
        'frequency_units' : 3600, # hour
    },
    {
        'function' : 'ecm.plugins.industry.tasks.industry.update_production_costs',
        'priority' : 0,
        'frequency' : 24,
        'frequency_units' : 3600, # hour
    },
]

URL_PERMISSIONS = [
    r'^/industry.*$',
]

SETTINGS = {
    'industry_group_name': 'Industry Team',
    'industry_internal_price_margin': 0.02,
    'industry_external_price_margin': 0.30,
    'industry_evecentral_url': 'http://api.eve-central.com/api/marketstat',
}


