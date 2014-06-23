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
# EVE Corporation Management. If not, see <>.

__author__ = 'Ajurna'
__date__ = "2013 8 08"

import logging

from ecm.apps.common import api
from ecm.apps.corp.models import Corporation, Alliance
from ecm.apps.corp.tasks.corp import fix_description

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def get_corp(corporationID):
    """
     corporationID: int
     :Corporation Object
    """
    try:
        return Corporation.objects.get(corporationID=corporationID)
    except Corporation.DoesNotExist:
        conn = api.eveapi.EVEAPIConnection()
        api_corp = conn.corp.CorporationSheet(corporationID=corporationID)
        LOG.info("Adding new Corporation: "+ str(api_corp.corporationName))
        corp = Corporation(corporationID   = api_corp.corporationID,
                           corporationName = str(api_corp.corporationName),
                           ticker          = api_corp.ticker,
                           ceoID           = api_corp.ceoID,
                           ceoName         = api_corp.ceoName,
                           stationID       = api_corp.stationID,
                           stationName     = api_corp.stationName,
                           description     = fix_description(api_corp.description),
                           taxRate         = api_corp.taxRate,
                           )
        if api_corp.allianceID:
            corp.alliance = get_alliance(api_corp.allianceID)
        corp.save()
        return corp

#------------------------------------------------------------------------------
def get_alliance(allianceID):
    """
     allianceID: int
    : Alliance object pulled from alliance list if needed
    """
    try:
        alliance = Alliance.objects.get(allianceID = allianceID)
    except Alliance.DoesNotExist:
        api_conn = api.eveapi.EVEAPIConnection()
        alliancesApi = api_conn.eve.AllianceList()
        alliance = Alliance()
        alliance.allianceID = allianceID
        for a in alliancesApi.alliances:
            if a.allianceID == allianceID:
                alliance.shortName = a.shortName
                alliance.name = a.name
                LOG.info("Adding new Alliance: "+ a.name)
                alliance.save()
                break
    return alliance

#------------------------------------------------------------------------------
def get_corp_or_alliance(entityID):
    """
     entityID:
    : Corp object if possible, alliance object if not.
    """
    if Corporation.objects.filter(corporationID=entityID):
        return Corporation.objects.get(corporationID=entityID)
    if Alliance.objects.filter(allianceID=entityID):
        return Alliance.objects.get(allianceID=entityID)
    
    try:
        return get_corp(entityID)
    except RuntimeError:
        #This is because at time of coding the api is broken and the only
        #way to catch this is by catching the eveapi runtime error
        #TODO: fix when ccp get their shit together.
        return get_alliance(entityID)