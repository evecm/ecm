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

from django.utils.translation import ugettext_lazy as tr_lazy

NAME = 'industry'
VERSION = '1.0'

DEPENDS_ON = {
    'ecm' : '2.0',
}

MENUS = [
    {'title': tr_lazy('Industry'),    'url': '',      'items': [
        {'title': tr_lazy('Orders'), 'url': 'orders/', 'items': []},
        {'title': tr_lazy('Jobs'), 'url': 'jobs/', 'items': []},
        {'title': tr_lazy('Catalog'), 'url': 'catalog/', 'items': [
            {'title': tr_lazy('Items'),         'url': 'catalog/items/'},
            {'title': tr_lazy('Supplies'),      'url': 'catalog/supplies/'},
            {'title': tr_lazy('Blueprints'),    'url': 'catalog/blueprints/'},
        ]},
    ]},
]

TASKS = [
    {
        'function' : 'ecm.plugins.industry.tasks.industry.update_supply_prices',
        'priority' : 0,
        'frequency' : 1,
        'frequency_units' : 60 * 60 * 24, # day
    },
    {
        'function' : 'ecm.plugins.industry.tasks.industry.update_all_production_costs',
        'priority' : 0,
        'frequency' : 1,
        'frequency_units' : 60 * 60 * 24, # day
    },
]

URL_PERMISSIONS = [
    r'^/industry/.*$',
]

SETTINGS = {
    'industry_group_name': 'Industry Team',
    'industry_default_margin': 0.30,
    'industry_default_price_source': 30000142,  # Jita
    'industry_evecentral_url': 'http://api.eve-central.com/api/marketstat',
}


