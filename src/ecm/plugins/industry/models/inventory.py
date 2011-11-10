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

from ecm.core.eve import db


#------------------------------------------------------------------------------
class SupplyPrice(models.Model):

    class Meta:
        app_label = 'industry'
        ordering = ['typeID']

    typeID = models.PositiveIntegerField(primary_key=True)
    price = models.FloatField()
    autoUpdate = models.BooleanField(default=True)

    def save(self, force_insert=False, force_update=False, using=None):
        models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using)
        PriceHistory.objects.create(typeID=self.typeID, price=self.price)

    def item_admin_display(self):
        name, _ = db.resolveTypeName(self.typeID)
        return name
    item_admin_display.short_description = 'Item'

#------------------------------------------------------------------------------
class PriceHistory(models.Model):

    class Meta:
        app_label = 'industry'
        verbose_name = "Price History"
        verbose_name_plural = "Prices History"
        ordering = ['typeID', 'date']

    typeID = models.PositiveIntegerField()
    price = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def item_admin_display(self):
        name, _ = db.resolveTypeName(self.typeID)
        return name
    item_admin_display.short_description = 'Item'
