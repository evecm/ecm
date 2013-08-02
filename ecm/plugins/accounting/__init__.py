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

NAME = 'accounting'
VERSION = '2.0'

DEPENDS_ON = {
    'ecm' : '2.0',
}

MENUS = [
     {'title': tr_lazy('Accounting'),    'url': '',      'items': [
        {'title': tr_lazy('Wallets Journal'), 'url': 'journal/', 'items': []},
        {'title': tr_lazy('Wallets Transactions'), 'url': 'transactions/', 'items': []},
        {'title': tr_lazy('Tax Contributions'), 'url': 'contributions/', 'items': []},
        {'title': tr_lazy('Contracts'), 'url': 'contracts/', 'items': []},
        {'title': tr_lazy('Market Orders'), 'url': 'marketorders/', 'items': []},
        {'title': tr_lazy('Report'), 'url': 'report/', 'items': []},
    ]},
]

TASKS = [
    {
        'function' : 'ecm.plugins.accounting.tasks.reftypes.update',
        'priority' : 100,
        'frequency' : 7,
        'frequency_units' : 60 * 60 * 24, # day
    }, {
        'function' : 'ecm.plugins.accounting.tasks.wallets.update',
        'priority' : 0,
        'frequency' : 6,
        'frequency_units' : 60 * 60, # hour
    }, {
        'function' : 'ecm.plugins.accounting.tasks.contracts.update',
        'priority' : 0,
        'frequency' : 6,
        'frequency_units' : 60 * 60, # hour
    }, {
        'function' : 'ecm.plugins.accounting.tasks.marketorders.update',
        'priority' : 0,
        'frequency' : 6,
        'frequency_units' : 60 * 60, # hour
    },
]

URL_PERMISSIONS = [
    r'^/accounting/.*$',
]
