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

from ecm.apps.eve.models import Type


#------------------------------------------------------------------------------
class SupplySource(models.Model):

    class Meta:
        app_label = 'industry'

    location_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return unicode(self.name)

#------------------------------------------------------------------------------
class Supply(models.Model):

    class Meta:
        app_label = 'industry'
        verbose_name_plural = 'Supplies'

    typeID = models.PositiveIntegerField(primary_key=True)
    price = models.FloatField(default=0.0)
    auto_update = models.BooleanField(default=True)
    supply_source = models.ForeignKey('SupplySource', related_name='prices', default=1)
    __item = None

    def update_price(self, newPrice):
        self.price = newPrice
        self.save()
        self.price_histories.create(price=self.price)

    def item_admin_display(self):
        return self.typeName
    item_admin_display.short_description = 'Item'

    @property
    def url(self):
        return '/industry/catalog/supplies/%d/' % self.typeID

    @property
    def permalink(self):
        return '<a href="%s" class="catalog-supply">%s</a>' % (self.url, self.typeName)

    def __unicode__(self):
        return unicode(self.typeName)

    def __hash__(self):
        return self.typeID

    def __getattr__(self, attrName):
        try:
            if self.__item is not None:
                return getattr(self.__item, attrName)
            else:
                self.__item = Type.objects.get(pk=self.typeID)
                return getattr(self.__item, attrName)
        except AttributeError:
            return models.Model.__getattribute__(self, attrName)

#------------------------------------------------------------------------------
class PriceHistory(models.Model):

    class Meta:
        app_label = 'industry'
        verbose_name = "Price History"
        verbose_name_plural = "Prices History"

    supply = models.ForeignKey('Supply', related_name='price_histories')
    price = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def item_admin_display(self):
        name = Type.objects.get(typeID = self.supply_id).typeName
        return name
    item_admin_display.short_description = 'Item'
