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

#------------------------------------------------------------------------------
class Hangar(models.Model):
    hangarID = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    accessLvl = models.PositiveIntegerField(default=1000)

    def __unicode__(self):
        return self.name

#------------------------------------------------------------------------------
class Wallet(models.Model):
    walletID = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    accessLvl = models.PositiveIntegerField(default=1000)
    
    def __unicode__(self):
        return self.name
    
    def get_url(self):
        return "/accounting/wallet/%d" % self.walletID
    
    def permalink(self):
        return '<a href="%s" class="wallet" >%s</a>' % (self.get_url(), self.name)

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
    description = models.CharField(max_length=2048)
    taxRate = models.PositiveIntegerField()
    memberLimit = models.PositiveIntegerField()
    
    def __unicode__(self):
        return self.corporationName
    
    
