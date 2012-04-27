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


NAME = 'accounting'
VERSION = '2.0'

DEPENDS_ON = {
    'ecm' : '2.0',
}

MENUS = [
     {'title': 'Accounting',    'url': '',      'items': [
        {'title': 'Wallets Journal', 'url': 'journal/', 'items': []},
        {'title': 'Tax Contributions', 'url': 'contributions/', 'items': []},
        {'title': 'Contracts', 'url': 'contracts/', 'items': []},
        {'title': 'Market Orders', 'url': 'marketorders/', 'items': []},
        {'title': 'Report', 'url': 'report/', 'items': []},
    ]},
]

TASKS = [
    {
        'function' : 'ecm.plugins.accounting.tasks.reftypes.update',
        'priority' : 100,
        'frequency' : 7,
        'frequency_units' : 86400, # day
    }, {
        'function' : 'ecm.plugins.accounting.tasks.wallets.update',
        'priority' : 0,
        'frequency' : 6,
        'frequency_units' : 3600, # hour
    }, {
        'function' : 'ecm.plugins.accounting.tasks.contracts.update',
        'priority' : 0,
        'frequency' : 6,
        'frequency_units' : 3600, # hour
    }, {
        'function' : 'ecm.plugins.accounting.tasks.marketorders.update',
        'priority' : 0,
        'frequency' : 6,
        'frequency_units' : 3600, # hour
    },
]

URL_PERMISSIONS = [
    r'^/accounting/.*$',
]
