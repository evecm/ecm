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

__date__ = "2010-02-08"
__author__ = "diabeteman"

from django.db import models

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

    def __unicode__(self):
        return unicode(self.name)

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

    class Meta:
        get_latest_by = 'id'
        ordering = ['id']

    def __unicode__(self):
        return unicode(self.corporationName)

class Standings(models.Model):
    
    class Meta:
        ordering = ['standing']
    
    contactID = models.BigIntegerField(default=0)
    is_corp_contact = models.BooleanField(default=True)
    contactName = models.CharField(max_length=50)
    standing = models.IntegerField(default=0)
    
    @property
    def contact_type(self):
        #https://forums.eveonline.com/default.aspx?g=posts&m=716708#post716708
        #Characters: ]90000000, 98000000[
        #Corporations: ]98000000, 99000000[
        #Alliances: ]99000000, 100000000[
        #Note: This is not accurate and should not be used until a better solution is found.
        if self.contactID > 90000000 and self.contactID < 98000000:
            return 'Character'
        elif self.contactID > 98000000 and self.contactID < 99000000:
            return 'Corporation'
        elif self.contactID > 99000000 and self.contactID < 100000000:
            return 'Alliance'
        else:
            return unicode(self.contactID)
    def __unicode__(self):
        return unicode(self.contactName)
