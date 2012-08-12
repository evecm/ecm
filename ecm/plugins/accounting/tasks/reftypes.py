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

__date__ = "2010-03-29"
__author__ = "diabeteman"

import logging

from django.db import transaction
from django.utils import timezone

from ecm.apps.common import api
from ecm.plugins.accounting.models import EntryType

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update():
    LOG.info("fetching /eve/RefTypes.xml.aspx...")
    # connect to eve API
    api_conn = api.connect()
    # retrieve /corp/CorporationSheet.xml.aspx
    typesApi = api_conn.eve.RefTypes()
    api.check_version(typesApi._meta.version)

    currentTime = timezone.make_aware(typesApi._meta.currentTime, timezone.utc)
    cachedUntil = timezone.make_aware(typesApi._meta.cachedUntil, timezone.utc)
    LOG.debug("current time : %s", str(currentTime))
    LOG.debug("cached util : %s", str(cachedUntil))
    LOG.debug("parsing api response...")

    for refType in typesApi.refTypes:
        entryType = EntryType()
        entryType.refTypeID = refType.refTypeID
        entryType.refTypeName = refType.refTypeName
        entryType.save()

    LOG.info("transaction types updated")



