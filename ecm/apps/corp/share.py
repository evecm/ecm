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

__date__ = '2012 08 01'
__author__ = 'diabeteman'

import logging

from django.db import transaction

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def process_details(corp, data):
    corp.set_corp_details(data)
    corp.save()
    LOG.info('Updated %r corp details' % corp)

#------------------------------------------------------------------------------
def process_alliance_standings(corp, data):
    process_corp_standings(corp, data, is_corp=False)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def process_corp_standings(corp, data, is_corp=True):
    
    corp.standings.filter(is_corp_contact=is_corp).delete()
    
    for standing in data:
        corp.standings.create(is_corp_contact=is_corp,
                              contactID=standing['contactID'],
                              contactName=standing['contactName'],
                              value=standing['value'],
                              )
    
    LOG.info('Updated %r %s standings' % (corp, is_corp and 'corp' or 'alliance'))
        