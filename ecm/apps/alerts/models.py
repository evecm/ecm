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

__date__ = "2012-08-09"
__author__ = "ajurna"


import logging

from django.utils.translation import ugettext as tr
from django.db import models
from django.contrib.auth.models import User, Group

from ecm.apps.scheduler.validators import FunctionValidator

LOG = logging.getLogger(__name__)

TYPES = {
    0: 'systematic',
    1: 'conditional',
    2: 'both',
}

#------------------------------------------------------------------------------
class ObserverSpec(models.Model):
    """
    This is where the observers are defined.you copy these to observers with 
    their details filled out to actually watch what you want to watch
    """
    class Meta:
        verbose_name = tr("Observer spec")
        verbose_name_plural = tr("Observer specs")

    name = models.CharField(max_length=256)
    description = models.CharField(max_length=256)
    handler_function = models.CharField(max_length=256, validators=[FunctionValidator()])
    callback_function = models.CharField(max_length=256, validators=[FunctionValidator()])
    arguments_spec = models.TextField(blank=True)
    notification_type = models.SmallIntegerField(choices=TYPES.items(), default=0)

class Observer(models.Model):
    """
    These are active observers that will be checked when they are called.
    """
    class Meta:
        verbose_name = tr("Observer")
        verbose_name = tr("Observers")
        
    observer_spec = models.ForeignKey(ObserverSpec, related_name="observers")
    arguments = models.TextField(blank=True)
    notification_type = models.SmallIntegerField(choices=TYPES.items(), default=0)
    users = models.ManyToManyField(User, related_name="users", blank=True)
    groups = models.ManyToManyField(Group, related_name='groups', blank=True)
    last_scan = models.DateTimeField(auto_now_add=True)
