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

__date__ = "2010-02-08"
__author__ = "diabeteman"

from django.db import models
from ecm.core.utils import print_float

#------------------------------------------------------------------------------
class Hangar(models.Model):

    class Meta:
        ordering = ['hangarID']

    hangarID = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    accessLvl = models.PositiveIntegerField(default=1000)

    def __unicode__(self):
        return unicode(self.name)

#------------------------------------------------------------------------------
class Wallet(models.Model):

    class Meta:
        ordering = ['walletID']

    walletID = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    accessLvl = models.PositiveIntegerField(default=1000)

    LINK = '<a href="%s" class="wallet" title="%s">%s</a>'

    def __unicode__(self):
        return unicode(self.name)

    @property
    def url(self):
        return "/accounting/wallet/%d" % self.walletID

    @property
    def permalink(self):
        return Wallet.LINK % (self.url, "Click for details on this wallet", self.name)

    def get_journal_url(self):
        return "/accounting/journal?walletID=%d" % self.walletID

    def permalink_to_journal(self, balance=None):
        if balance is None:
            name = self.name
        else:
            name = print_float(balance)
        return Wallet.LINK % (self.get_journal_url(), "Click to access this wallet's journal", name)

#------------------------------------------------------------------------------
class Corp(models.Model):
    corporationID = models.BigIntegerField()
    corporationName = models.CharField(max_length=256)
    ticker = models.CharField(max_length=8)
    ceoID = models.BigIntegerField()
    ceoName = models.CharField(max_length=256)
    stationID = models.BigIntegerField()
    stationName = models.CharField(max_length=256)
    allianceID = models.BigIntegerField()
    allianceName = models.CharField(max_length=256)
    allianceTicker = models.CharField(max_length=8)
    description = models.TextField()
    taxRate = models.PositiveIntegerField()
    memberLimit = models.PositiveIntegerField()

    def __unicode__(self):
        return unicode(self.corporationName)


