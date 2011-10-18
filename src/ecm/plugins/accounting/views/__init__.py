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


from ecm.core.utils import print_float

WALLET_LINK = '<a href="%s" class="wallet" title="%s">%s</a>'

#------------------------------------------------------------------------------
def wallet_url(wallet):
    return "/accounting/wallet/%d/" % wallet.walletID
#------------------------------------------------------------------------------
def wallet_journal_url(wallet):
    return "/accounting/journal?walletID=%d" % wallet.walletID
#------------------------------------------------------------------------------
def wallet_permalink(wallet):
    return WALLET_LINK % (wallet.url, "Click for details on this wallet",
                          wallet.name)
#------------------------------------------------------------------------------
def wallet_journal_permalink(wallet, balance=None):
    if balance is None:
        name = wallet.name
    else:
        name = print_float(balance)
    return WALLET_LINK % (wallet.get_journal_url(),
                          "Click to access this wallet's journal", name)
