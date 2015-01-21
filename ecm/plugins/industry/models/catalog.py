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
from ecm.utils import format

__date__ = "2015 1 21"
__author__ = "diabeteman"

from django.db import models
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as tr
from django.core.validators import MaxValueValidator, MinValueValidator

from ecm.apps.common.models import Setting
from ecm.apps.eve.models import Type, BlueprintType

#------------------------------------------------------------------------------
class CatalogEntry(models.Model):
    """
    Represents a EVE item that can be manufactured with a blueprint.
    
    Extra fields are available to integrate it into the industry/shop system.
    """
    
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
            if skip_invented and bp.product.metaGroupID == 2 and bp.parentBlueprintTypeID is not None:
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
    """
    Represents a EVE blueprint owned by the corporation.
    
    It has a link to a CatalogEntry and carries variable data of blueprints (ME, PE, etc.)
    """
    
    class Meta:
        app_label = 'industry'
        get_latest_by = 'id'

    typeID = models.IntegerField()
    me = models.SmallIntegerField(default=0, validators=[MinValueValidator(0),MaxValueValidator(10)])
    pe = models.SmallIntegerField(default=0,  validators=[MinValueValidator(0),MaxValueValidator(20)])
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

#------------------------------------------------------------------------------
class ItemGroup(models.Model):
    """
    Represents a user-defined logical ensemble of items.
    
    An ItemGroup will be used in along with PricingPolicy to associate margins to items.
    
    NB: A single item can be in multiple groups. 
    """
    
    class Meta:
        app_label = 'industry'
    
    name = models.CharField(max_length=100, unique=True)
    items = models.ManyToManyField(CatalogEntry, related_name='item_groups')

    def item_count(self):
        return self.items.all().count()

    def __unicode__(self):
        return self.name

#------------------------------------------------------------------------------
class PricingPolicy(models.Model):
    """
    Stores a pricing policy for a combination of (item_group, user_group).
    
    surcharge_relative 
        a percentage of the price that should be considered as a surcharge
    surcharge_absolute 
        a fixed amount of iSK that should be added to the total surcharge
    
    Price calculation
    -----------------
        
        >>> total_surcharge = production_cost * surcharge_relative + surcharge_absolute
        >>> sell_price = production_cost + total_surcharge
    
    Special Values Meaning
    ----------------------
    
        >>> item_group = None    # means  "all items" 
        >>> user_group = None    # means  "all users"
    """
    
    class Meta:
        app_label = 'industry'
        verbose_name = tr("Surcharge Policy")
        verbose_name_plural = tr("Surcharge Policies")
    
    is_active = models.BooleanField(default=True)
    item_group = models.ForeignKey(ItemGroup, blank=True, null=True, default=None)
    user_group = models.ForeignKey(Group, blank=True, null=True, default=None)
    surcharge_relative = models.FloatField(default=0.0) # a percentage
    surcharge_absolute = models.FloatField(default=0.0) # fixed amount of iSK
    priority = models.SmallIntegerField(default=0)
    
    @staticmethod
    def resolve_surcharge(item, user, price):
        active_policies = PricingPolicy.objects.filter(is_active=True)
        
        if active_policies.filter(user_group__in=user.groups.all()):
            policies = active_policies.filter(user_group__in=user.groups.all())
        else:
            # if no policy matches the user's groups, we use only non group-based policies
            policies = active_policies.filter(user_group__isnull=True)
        
        if policies.filter(item_group__in=item.item_groups.all()):
            policies = policies.filter(item_group__in=item.item_groups.all())
        else:
            # if no policy matches the item, we use only non item-based policies
            policies = policies.filter(item_group__isnull=True)
        
        if policies:
            policies = policies.extra(
                select={'total_surcharge': '%s * surcharge_relative + surcharge_absolute'},
                select_params=(price,),
            )
            policies = policies.order_by('-priority', 'total_surcharge')
            surcharge = policies[0].total_surcharge # take the smallest surcharge
        else:
            # If no policy is defined for this (item, user) combination,
            # we fallback to the default margin.
            surcharge = Setting.get('industry_default_margin') * price
        
        return surcharge
    
    def surcharge_relative_admin_display(self):
        return '%d %%' % round(self.surcharge_relative * 100)
    surcharge_relative_admin_display.short_description = 'Relative surcharge'
    
    def surcharge_absolute_admin_display(self):
        return '%s iSK' % format.print_float(self.surcharge_absolute)
    surcharge_absolute_admin_display.short_description = 'Fixed surcharge'
    
    
    