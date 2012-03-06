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
__date__ = "2012 3 6"
__author__ = "Ajurna"

from django.db import models

from ecm.lib import bigintpatch #@UnusedImport

from ecm.apps.hr.models.member import Member

from ecm.core.eve.db import get_type_name

class CharacterSheet(models.Model):
    member = models.ForeignKey(Member)
    characterID = models.IntegerField()
    name = models.CharField(max_length=128)
    DoB = models.CharField(max_length=128)
    race = models.CharField(max_length=128)
    bloodLine = models.CharField(max_length=128)
    ancestry = models.CharField(max_length=128)
    gender = models.CharField(max_length=128)
    corporationName = models.CharField(max_length=128)
    corporationID = models.IntegerField()
    allianceName = models.CharField(max_length=128, null=True, blank=True)
    allianceID = models.IntegerField(blank=True, null=True)
    cloneName = models.CharField(max_length=128)
    CloneSkillPoints = models.IntegerField()
    balance = models.DecimalField(max_digits=20, decimal_places=2)
    memoryBonusName = models.CharField(max_length=128, blank=True, null=True)
    memoryBonusValue = models.IntegerField(blank=True, null=True)
    intelligenceBonusName = models.CharField(max_length=128, blank=True, null=True)
    intelligenceBonusValue = models.IntegerField(blank=True, null=True)
    charismaBonusName = models.CharField(max_length=128, blank=True, null=True)
    charismaBonusValue = models.IntegerField(blank=True, null=True)
    willpowerBonusName = models.CharField(max_length=128, blank=True, null=True)
    willpowerBonusValue = models.IntegerField(blank=True, null=True)
    perceptionBonusName = models.CharField(max_length=128, blank=True, null=True)
    perceptionBonusValue = models.IntegerField(blank=True, null=True)
    intelligence = models.IntegerField()
    memory = models.IntegerField()
    charisma = models.IntegerField()
    perception = models.IntegerField()
    willpower = models.IntegerField()
    def __unicode__(self):
        return unicode(self.name)

#------------------------------------------------------------------------------
class skills(models.Model):
    character = models.ForeignKey(CharacterSheet)
    typeID = models.IntegerField()
    skillpoints = models.IntegerField()
    level = models.IntegerField()
    def __unicode__(self):
        return self.name()
    def name(self):
        name = get_type_name(self.typeID)
        return unicode(name[0])
