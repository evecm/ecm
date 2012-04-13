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
from django.utils.translation import ugettext_lazy as tr

from ecm.apps.eve.models import Type, BlueprintType


#------------------------------------------------------------------------------
class CatalogEntry(models.Model):

    class Meta:
        app_label = 'industry'
        verbose_name = tr("Catalog Entry")
        verbose_name_plural = tr("Catalog Entries")

    typeID = models.IntegerField(primary_key=True)
    typeName = models.CharField(max_length=100)
    fixed_price = models.FloatField(null=True, blank=True)
    production_cost = models.FloatField(null=True, blank=True)
    public_price = models.FloatField(null=True, blank=True)
    last_update = models.DateTimeField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    __item = None

    @property
    def url(self):
        return '/industry/catalog/items/%d/' % self.typeID

    @property
    def permalink(self):
        return '<a href="%s" class="catalog-item">%s</a>' % (self.url, self.typeName)

    def missing_blueprints(self, skip_invented=True):
        involved_bps = set()
        for bp in self.blueprint.get_involved_blueprints(recurse=True) | set([self.blueprint]):
            if skip_invented and bp.product.techLevel == 2 and bp.parentBlueprintTypeID is not None:
                continue
            else:
                involved_bps.add(bp)
        involved_bp_ids = [ bp.typeID for bp in involved_bps ]
        owned_bps = set(OwnedBlueprint.objects.filter(typeID__in=involved_bp_ids))
        return involved_bps - owned_bps

    def __getattr__(self, attr):
        try:
            if self.__item is None:
                self.__item = Type.objects.get(pk=self.typeID)
            return getattr(self.__item, attr)
        except AttributeError:
            return models.Model.__getattribute__(self, attr)

    def __unicode__(self):
        return unicode(self.typeName)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return self.typeID


#------------------------------------------------------------------------------
class OwnedBlueprint(models.Model):

    class Meta:
        app_label = 'industry'
        ordering = ['typeID', '-me']
        get_latest_by = 'id'

    typeID = models.IntegerField()
    me = models.SmallIntegerField(default=0)
    pe = models.SmallIntegerField(default=0)
    copy = models.BooleanField(default=False)
    runs = models.SmallIntegerField(default=0)
    invented = models.BooleanField(default=False)
    catalog_entry = models.ForeignKey(CatalogEntry, related_name='blueprints', null=True, blank=True)
    __blueprint = None

    @property
    def url(self):
        return '/industry/catalog/blueprints/%d/' % self.id

    @property
    def permalink(self):
        return '<a href="%s" class="catalog-blueprint">%s</a>' % (self.url, self.typeName)

    @property
    def is_original(self):
        return not self.copy

    def bill_of_materials(self, activity, runs=1, round_result=False):
        return self.get_bill_of_materials(activity, runs, self.me, round_result)

    def manufacturing_time(self, runs=1):
        return self.get_duration(runs=runs, pe_level=self.pe, activity=BlueprintType.Activity.MANUFACTURING)

    def pe_research_time(self, runs=1):
        return self.get_duration(runs=runs, activity=BlueprintType.Activity.RESEARCH_PE)

    def me_research_time(self, runs=1):
        return self.get_duration(runs=runs, activity=BlueprintType.Activity.RESEARCH_ME)

    def copy_time(self, runs=1):
        return self.get_duration(runs=runs, activity=BlueprintType.Activity.COPY)

    def invention_time(self, runs=1):
        return self.get_duration(runs=runs, activity=BlueprintType.Activity.INVENTION)

    def item_name_admin_display(self):
        return self.typeName
    item_name_admin_display.short_description = 'Blueprint'

    def __getattr__(self, attr):
        try:
            if self.__blueprint is None:
                self.__blueprint = BlueprintType.objects.get(pk=self.typeID)
            return getattr(self.__blueprint, attr)
        except AttributeError:
            return models.Model.__getattribute__(self, attr)

    def __unicode__(self):
        return unicode(self.typeName)

    def __hash__(self):
        return self.typeID

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __cmp__(self, other):
        return cmp(self.typeID, other.typeID)
