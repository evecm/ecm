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


from datetime import timedelta

from django.conf import settings
from django.db import models

from ecm.core.eve import db
from ecm.data.industry.models.job import Job

#------------------------------------------------------------------------------
class MileStone(models.Model):
    """
    To simulate a Tailor-like process, 
    jobs are affected to MileStones which are 'fixed periodic delivery dates'.
    """
    
    class Meta:
        app_label = 'industry'
        verbose_name = "MileStone"
        verbose_name_plural = "MileStones"
        ordering = ['date']
    
    date = models.DateField(unique=True, auto_now_add=True)
    
    def next(self):
        next_date = self.date + timedelta(days=settings.MILESTONE_INTERVAL_DAYS)
        return MileStone.objects.get_or_create(date=next_date)
    
    def prev(self):
        prev_date = self.date - timedelta(days=settings.MILESTONE_INTERVAL_DAYS)
        return MileStone.objects.get_or_create(date=prev_date)


#------------------------------------------------------------------------------
class ProductionSite(models.Model):

    class Meta:
        app_label = 'industry'
        ordering = ['customName', 'locationID']
    
    
    locationID = models.BigIntegerField(primary_key=True)
    customName = models.CharField(max_length=255)
    discount = models.FloatField(default=0.0)

    def __unicode__(self):
        return u'%s (%s)' % (self.customName, self.real_name_admin_display())
    
    def real_name_admin_display(self):
        name, _ = db.resolveLocationName(self.locationID)
        return name
    real_name_admin_display.short_description = 'Real Name'

#------------------------------------------------------------------------------
class FactorySlot(models.Model):
    
    class Meta:
        app_label = 'industry'
        ordering = ['site', 'activity']
    
    site = models.ForeignKey('ProductionSite', related_name='slots')
    activity = models.SmallIntegerField(default=Job.MANUFACTURING, choices=Job.ACTIVITIES.items())
