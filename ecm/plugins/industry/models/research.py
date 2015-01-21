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

__date__ = "2015 1 21"
__author__ = "diabeteman"

import math

from django.db import models
from django.utils.translation import ugettext_lazy as tr

from ecm.apps.eve import formulas
from ecm.plugins.industry import constants
from ecm.plugins.industry.models.catalog import OwnedBlueprint

ME_CHOICES = []
for me_mod in constants.DECRYPTOR_ATTRIBUTES.keys():
    if me_mod is not None:
        ME_CHOICES.append( (me_mod, '%+d' % me_mod) )
    else:
        ME_CHOICES.append( (me_mod, 'None') )


class InventionError(Exception): pass

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
        verbose_name = tr("Invention Policy")
        verbose_name_plural = tr("Invention Policies")

    item_group_id = models.IntegerField(default=0)
    item_id = models.IntegerField(blank=True, null=True)
    item_group = models.CharField(max_length=255)
    encryption_skill_lvl = models.SmallIntegerField(default=5)
    science1_skill_lvl = models.SmallIntegerField(default=5)
    science2_skill_lvl = models.SmallIntegerField(default=5)
    me_mod = models.IntegerField(choices=ME_CHOICES, blank=True, null=True)

    def skills_admin_display(self):
        return '%s | %s %s' % (self.encryption_skill_lvl, self.science1_skill_lvl, self.science2_skill_lvl)
    skills_admin_display.short_description = 'Skills'

    def chance_mod_admin_display(self):
        return '%+d%%' % int(100 * constants.DECRYPTOR_ATTRIBUTES[self.me_mod][0] - 100)
    chance_mod_admin_display.short_description = 'Chance mod'

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
                              pe=pe,
                              invented=True)

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
        if blueprint.parent_blueprint is None:
            raise InventionError('Blueprint %s has no parent_blueprint and cannot be invented.', blueprint.blueprintTypeID)

        if InventionPolicy.objects.filter(item_id=blueprint.product.typeID):
            policy = InventionPolicy.objects.get(item_id=blueprint.product.typeID)
        elif InventionPolicy.objects.filter(item_group_id=blueprint.product.groupID):
            policy = InventionPolicy.objects.get(item_group_id=blueprint.product.groupID)
        else:
            # no specific policy defined for this blueprint,
            # fallback to the default policy (modules)
            policy = InventionPolicy.objects.get(item_group_id=-1)

        decriptorTypeID = None
        runs_mod = 0
        chance_mod = 1.0
        me = -2 # base ME for invented BPCs without decryptor
        pe = -4 # base PE for invented BPCs without decryptor
        for typeID, _chance, _me, _pe, _runs, _ in constants.DECRYPTOR_INFO:
            if policy.me_mod == _me:
                decriptorTypeID = typeID
                me += _me
                pe += _pe
                chance_mod = _chance
                runs_mod = _runs
                break
        runs_per_bp = formulas.invented_bpc_runs(blueprint.parent_blueprint.maxProductionLimit,
                                                 blueprint.parent_blueprint.maxProductionLimit,
                                                 blueprint.maxProductionLimit,
                                                 runs_mod)
        chance = formulas.calc_invention_chance(blueprint.parent_blueprint.inventionBaseChance,
                                                policy.encryption_skill_lvl,
                                                policy.science1_skill_lvl,
                                                policy.science2_skill_lvl,
                                                chance_mod)
        attempts = int(math.ceil(1.0 / chance))

        return runs_per_bp, me, pe, decriptorTypeID, attempts
