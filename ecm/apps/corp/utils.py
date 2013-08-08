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

__author__ = 'Ajurna'
__date__ = "2013 8 08"

import logging

from django.db import transaction

from ecm.apps.common import api
from ecm.apps.corp.models import Corporation, Alliance
from ecm.apps.corp.tasks.corp import fix_description

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def get_corp(corporationID):
    """
    @param corporationID: int
    @return :Corporation Object
    """
    try:
        return Corporation.objects.get(corporationID=corporationID)
    except Corporation.DoesNotExist:
        conn = api.eveapi.EVEAPIConnection()
        api_corp = conn.corp.CorporationSheet(corporationID=corporationID)
        LOG.info("Adding new Corporation: "+ api_corp.corporationName)
        return Corporation(corporationID   = api_corp.corporationID,
                           corporationName = api_corp.corporationName,
                           ticker          = api_corp.ticker,
                           ceoID           = api_corp.ceoID,
                           ceoName         = api_corp.ceoName,
                           stationID       = api_corp.stationID,
                           stationName     = api_corp.stationName,
                           description     = fix_description(api_corp.description),
                           alliance        = get_alliance_from_corp_api(api_corp),
                           taxRate         = api_corp.taxRate,
                           )

#------------------------------------------------------------------------------
@transaction.commit_on_success
def get_corpOrAlliance(corporationID):
    """
    @param corporationID:
    @return: Corp object if possible, alliance object if not.
    This was written for the mail plugin.
    """
    try:
        return Corporation.objects.get(corporationID=corporationID)
    except Corporation.DoesNotExist:
        conn = api.eveapi.EVEAPIConnection()
        try:
            api_corp = conn.corp.CorporationSheet(corporationID=corporationID)
        except RuntimeError:
            return pull_alliance_from_int(corporationID)
        try:
            alliance = Alliance.objects.get(allianceID = api_corp.allianceID)
        except Alliance.DoesNotExist:
            alliance = get_alliance_from_corp_api(api_corp)
        LOG.info("Adding new Corporation: "+ api_corp.corporationName)
        return Corporation(corporationID   = api_corp.corporationID,
                           corporationName = api_corp.corporationName,
                           ticker          = api_corp.ticker,
                           ceoID           = api_corp.ceoID,
                           ceoName         = api_corp.ceoName,
                           stationID       = api_corp.stationID,
                           stationName     = api_corp.stationName,
                           description     = fix_description(api_corp.description),
                           alliance        = alliance,
                           taxRate         = api_corp.taxRate,
                           )
#------------------------------------------------------------------------------
@transaction.commit_on_success
def get_alliance_from_corp_api(api_corp):
    """
    @param api_corp: api object of a corp
    @return: new alliance object created by corp api data
    """
    try:
        try:
            try:
                alliance = Alliance.objects.get(allianceID = api_corp.allianceID)
            except Alliance.DoesNotExist:
                LOG.info("Adding new Alliance: "+ api_corp.allianceName)
                alliance = Alliance()
                alliance.allianceID = api_corp.allianceID
                alliance.name = api_corp.allianceName
                alliancesApi = api.connect().eve.AllianceList()
                for a in alliancesApi.alliances:
                    if a.allianceID == api_corp.allianceID:
                        alliance.shortName = a.shortName
                        alliance.save()
                        break
        except api.Error:
            LOG.exception("Failed to fetch AllianceList.xml.aspx from EVE API server")
            alliance = None
    except:
        alliance = None
    return alliance

@transaction.commit_on_success
def pull_alliance_from_int(allianceID):
    """
    @param allianceID: int
    @return: Alliance object pulled from alliance list if needed
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