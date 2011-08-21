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

__date__ = "2011 8 20"
__author__ = "diabeteman"


from django.db import models
from django.utils.translation import ugettext_lazy as _

from ecm.core.eve import constants
from ecm.data.industry.models.catalog import OwnedBlueprint

#------------------------------------------------------------------------------
class InventionPolicy(models.Model):
    """
    An InventionPolicy defines two things for a specified item group: 
    
        - the average chance of obtaining a T2 BPC from an invention job
          (considering the skills of the invention crew)
        - the wanted ME of this BPC
    
    This allows to resolve which decryptor must be used to obtain a T2 BPC 
    that respects the InventionPolicy applied on the item's group. 
    """
    
    class Meta:
        app_label = 'industry'
        verbose_name = _("Invention Policy")
        verbose_name_plural = _("Invention Policies")
        ordering = ['targetME', 'itemGroupID']
    
    itemGroupID = models.IntegerField(primary_key=True)
    itemGroupName = models.CharField(max_length=255)
    inventionChance = models.FloatField()
    targetME = models.IntegerField()
        
    def invention_chance_admin_display(self):
        return unicode('{0:.0%}'.format(self.inventionChance))
    invention_chance_admin_display.short_description = "InventionChance"


    @staticmethod
    def attempts(blueprint):
        _, _, _, _, attempts = InventionPolicy.resolve(blueprint)
        return attempts
    
    @staticmethod
    def blueprint(blueprint):
        runsPerBp, me, pe, _, _ = InventionPolicy.resolve(blueprint)
        return OwnedBlueprint(blueprintTypeID=blueprint.typeID,
                              runs=runsPerBp,
                              copy=True,
                              me=me,
                              pe=pe)

    @staticmethod
    def decryptor(blueprint):
        _, _, _, decriptorTypeID, _ = InventionPolicy.resolve(blueprint)
        return decriptorTypeID


    @staticmethod
    def resolve(blueprint):
        """
        Resolve which decryptor and how many invention runs must be used 
        to invent the given blueprint
        
        If no decryptor is required, return None as the decryptor typeID 
        """
        decryptorGroup = constants.INTERFACES_DECRYPTOR_MAPPING[blueprint.parentBlueprint.dataInterfaceID]
        
        try:
            policy = InventionPolicy.objects.get(itemGroupID=blueprint.item.groupID)
        except InventionPolicy.DoesNotExist:
            # no specific policy defined for this blueprint, 
            # fallback to the default policy (modules)
            policy = InventionPolicy.objects.get(itemGroupID=0)
        
        decriptorTypeID = None
        chance = policy.inventionChance
        runsPerBp = 1
        me = -4 # base ME for invented BPCs without decryptor
        pe = -4 # base PE for invented BPCs without decryptor
        for typeID, chanceMod, meMod, peMod, runsMod, _ in constants.DECRYPTORS[decryptorGroup]:
            if policy.targetME == (me + meMod):
                decriptorTypeID = typeID
                chance *= chanceMod
                me += meMod
                pe += peMod
                runsPerBp += runsMod
                break
        attempts = int(round(1.0 / chance))
        
        return runsPerBp, me, pe, decriptorTypeID, attempts