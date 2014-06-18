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

__date__ = "2011 10 14"
__author__ = "diabeteman"

from django.conf.urls import patterns

urlpatterns = patterns('ecm.plugins.accounting.views',
    (r'^$',                              'wallets.wallets'),
    (r'^wallets/data/$',                 'wallets.wallets_data'),
    (r'^journal/$',                      'journal.journal'),
    (r'^journal/data/$',                 'journal.journal_data'),
    (r'^transactions/$',                 'transactions.transactions'),
    (r'^transactions/data/$',            'transactions.transactions_data'),
    (r'^contracts/$',                    'contracts.contracts'),
    (r'^contracts/data/$',               'contracts.contracts_data'),
    (r'^contracts/(\d+)/$',              'contracts.details'),
    (r'^contracts/(\d+)/data/$',         'contracts.details_data'),
    (r'^marketorders/$',                 'marketorders.marketorders'),
    (r'^marketorders/data/$',            'marketorders.marketorders_data'),
    (r'^contributions/$',                'contrib.member_contrib'),
    (r'^contributions/members/data/$',   'contrib.member_contrib_data'),
    (r'^contributions/players/data/$',   'contrib.player_contrib_data'),
    (r'^contributions/systems/data/$',   'contrib.system_contrib_data'),
    (r'^contributions/total/data/$',     'contrib.total_contrib_data'),
    (r'^report/$',                       'report.report'),
)
