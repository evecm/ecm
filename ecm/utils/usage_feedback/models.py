# Copyright (c) 2010-2013 Robin Jarry
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

__date__ = "2013 07 17"
__author__ = "diabeteman"

import logging

from django.db import models

LOG = logging.getLogger(__name__)


class ECMInstanceFeedback(models.Model):

    key_fingerprint = models.CharField(max_length=200, primary_key=True)
    public_key = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=200, blank=True, null=True)

    # corp_id is not primary_key here, we focus on "instances" more than
    # on "corporations" there could be multiple instances of ecm running
    # for the same corp.
    corp_id = models.BigIntegerField(blank=True, null=True)
    corp_name = models.CharField(max_length=256, blank=True, null=True)

    eve_char_count = models.IntegerField(default=0)
    active_user_count = models.IntegerField(default=0)
    avg_last_visit_top10 = models.IntegerField(default=0)
    avg_last_visit = models.IntegerField(default=0)
    first_installed = models.DateTimeField(blank=True, null=True)

    country_code = models.CharField(max_length=2, blank=True, null=True)
    country_name = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)

    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    last_updated = models.DateTimeField(auto_now=True)
    feedback_count = models.IntegerField(default=0)

    def __hash__(self):
        return hash(self.key_fingerprint)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.key_fingerprint == self.key_fingerprint

    def __unicode__(self):
        return self.corp_name
