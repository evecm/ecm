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

__date__ = "2011 8 20"
__author__ = "diabeteman"

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ecm.plugins.industry import constants
from ecm.plugins.industry.models.catalog import OwnedBlueprint

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
        ordering = ['target_me', 'item_group_id']

    item_group_id = models.IntegerField(primary_key=True)
    item_group = models.CharField(max_length=255)
    invention_chance = models.FloatField()
    target_me = models.IntegerField()

    def invention_chance_admin_display(self):
        return '%d' % (self.invention_chance * 100.0)
    invention_chance_admin_display.short_description = "InventionChance"


    @staticmethod
    def attempts(blueprint):
        _, _, _, _, attempts = InventionPolicy.resolve(blueprint)
        return attempts

    @staticmethod
    def blueprint(blueprint):
        runs_per_bp, me, pe, _, _ = InventionPolicy.resolve(blueprint)
        return OwnedBlueprint(typeID=blueprint.blueprintTypeID,
                              runs=runs_per_bp,
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
        decryptor_group = constants.INTERFACES_DECRYPTOR_MAPPING[blueprint.parent_blueprint.dataInterfaceID]

        try:
            policy = InventionPolicy.objects.get(item_group_id=blueprint.product.groupID)
        except InventionPolicy.DoesNotExist:
            # no specific policy defined for this blueprint,
            # fallback to the default policy (modules)
            policy = InventionPolicy.objects.get(item_group_id=0)

        decriptorTypeID = None
        chance = policy.invention_chance
        runs_per_bp = 1
        me = -4 # base ME for invented BPCs without decryptor
        pe = -4 # base PE for invented BPCs without decryptor
        for typeID, chance_mod, me_mod, pe_mod, runs_mod, _ in constants.DECRYPTOR_INFO[decryptor_group]:
            if policy.target_me == (me + me_mod):
                decriptorTypeID = typeID
                # Max Skill mod.
                skill_enc = 5
                skill_data = 5
                skill_data_2 = 5
                chance = chance * (1+(0.01 * skill_enc))*(1+((skill_data+skill_data_2)*0.1/5)) * chance_mod
                # chance *= chance_mod
                me += me_mod
                pe += pe_mod
                
                runs_per_bp += runs_mod
                break
        attempts = 1.0 / chance

        return runs_per_bp, me, pe, decriptorTypeID, attempts
