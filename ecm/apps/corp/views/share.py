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

from ecm.apps.corp.models import Corporation
from ecm.apps.corp.views.auth import valid_session_required, encrypted_response

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@valid_session_required
def list_allowed_shares(request):
    LOG.info('Corporation: "%s" (id: %s) has requested allowed shared data' 
                                    % (request.corp, request.corp.corporationID))
    allowed_urls = [ share.url for share in request.corp.get_allowed_shares() ]
    return encrypted_response(request, allowed_urls)

#------------------------------------------------------------------------------
@valid_session_required
def details(request):
    LOG.info('Corporation: "%s" (id: %s) has requested our corp details' 
                                    % (request.corp, request.corp.corporationID))
    data = Corporation.objects.mine().get_corp_details()
    return encrypted_response(request, data)
    
#------------------------------------------------------------------------------
@valid_session_required
def corp_standings(request):
    LOG.info('Corporation: "%s" (id: %s) has requested our corp standings' 
                                    % (request.corp, request.corp.corporationID))
    
    standings = Corporation.objects.mine().standings.filter(is_corp_contact=True)
    data = list(standings.values('contactID', 'contactName', 'value'))
    return encrypted_response(request, data, compress=True)
    
#------------------------------------------------------------------------------
@valid_session_required
def alliance_standings(request):
    LOG.info('Corporation: "%s" (id: %s) has requested our alliance standings' 
                                    % (request.corp, request.corp.corporationID))
    
    standings = Corporation.objects.mine().standings.filter(is_corp_contact=False)
    data = list(standings.values('contactID', 'contactName', 'value'))
    return encrypted_response(request, data, compress=True)
    
