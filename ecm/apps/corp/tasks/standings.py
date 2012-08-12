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

__date__ = "2012-04-26"
__author__ = "ajurna"

from django.db import transaction
from django.utils import timezone

from ecm.apps.corp.models import Standing, Corporation
from ecm.apps.common.models import UpdateDate
from ecm.apps.common import api

import logging
LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update():
    """
    Fetch a /corp/ContactList.xml.aspx api response, parse it and store it to
    the database.
    """
    LOG.info("fetching /corp/ContactList.xml.aspx...")
    api_conn = api.connect()
    corpApi = api_conn.corp.ContactList(characterID=api.get_charID())
    api.check_version(corpApi._meta.version)
    currentTime = timezone.make_aware(corpApi._meta.currentTime, timezone.utc)
    
    my_corp = Corporation.objects.mine()
    
    # clean existing standings first
    Standing.objects.filter(corp=my_corp).delete()
    
    for contact in corpApi.corporateContactList:
        Standing.objects.create(corp=my_corp,
                                contactID=contact.contactID,
                                is_corp_contact=True,
                                contactName=contact.contactName,
                                value=contact.standing,
                                )
    
    for contact in corpApi.allianceContactList: 
        Standing.objects.create(corp=my_corp,
                                contactID=contact.contactID,
                                is_corp_contact=False,
                                contactName=contact.contactName,
                                value=contact.standing,
                                )
        
    UpdateDate.mark_updated(model=Standing, date=currentTime)
    LOG.info("corp standings updated")
