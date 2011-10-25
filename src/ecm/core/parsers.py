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

from __future__ import with_statement

__date__ = "2010-02-08"
__author__ = "diabeteman"

import threading

from django.contrib.auth.models import Group
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from ecm.apps.hr.models import RoleType, Role
from ecm import settings
from ecm.apps.common.models import UpdateDate

#------------------------------------------------------------------------------
def checkApiVersion(version):
    if version != settings.EVE_API_VERSION:
        raise DeprecationWarning("Wrong EVE API version. "
                "Expected '%s', got '%s'." % (settings.EVE_API_VERSION, version))

#------------------------------------------------------------------------------
def calcDiffs(oldItems, newItems):
    """
    Quick way to compare 2 hashtables.

    This method returns 2 lists, added and removed items
    when comparing the old and the new set
    """

    removed  = []
    added    = []

    for item in oldItems.values():
        try:
            newItems[item] # is "item" still in the newItems?
        except KeyError: # KeyError -> "item" has disappeared
            removed.append(item)
    for item in newItems.values():
        try:
            oldItems[item] # was "item" in the oldItems already?
        except KeyError: # KeyError -> "item" is new
            added.append(item)

    return removed, added

#------------------------------------------------------------------------------
def markUpdated(model, date):
    """
    Tag a model's table in the database as 'updated'
    With the update date and the previous update date as well.
    """
    try:
        update = UpdateDate.objects.get(model_name=model.__name__)
        if not update.update_date == date:
            update.prev_update = update.update_date
            update.update_date = date
            update.save()
    except ObjectDoesNotExist:
        update = UpdateDate(model_name=model.__name__, update_date=date).save()
    except MultipleObjectsReturned:
        raise Exception
