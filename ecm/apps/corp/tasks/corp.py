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

__date__ = "2010-02-08"
__author__ = "diabeteman"


import re

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from ecm.lib import eveapi
from ecm.apps.common.models import UpdateDate
from ecm.apps.corp.models import Corp, Hangar, Wallet
from ecm.apps.eve import api

import logging
LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update():
    """
    Fetch a /corp/CorporationSheet.xml.aspx api response, parse it and store it to
    the database.
    """
    LOG.info("fetching /corp/CorporationSheet.xml.aspx...")
    # connect to eve API
    api_conn = api.connect()
    # retrieve /corp/CorporationSheet.xml.aspx
    corpApi = api_conn.corp.CorporationSheet(characterID=api.get_charID())
    api.check_version(corpApi._meta.version)

    currentTime = corpApi._meta.currentTime

    LOG.debug("parsing api response...")
    corp = update_corp_info(corpApi, currentTime)

    LOG.debug("name: %s [%s]", corp.corporationName, corp.ticker)
    LOG.debug("alliance: %s <%s>", corp.allianceName, corp.allianceTicker)
    LOG.debug("CEO: %s", corpApi.ceoName)
    LOG.debug("tax rate: %d%%", corp.taxRate)
    LOG.debug("member limit: %d", corp.memberLimit)

    update_hangar_divisions(corpApi, currentTime)
    update_wallet_divisions(corpApi, currentTime)

    LOG.info("corp info updated")

#------------------------------------------------------------------------------
def update_corp_info(corpApi, currentTime):
    try:
        try:
            allianceName = corpApi.allianceName
            allianceID   = corpApi.allianceID
            allianceTicker = ""
            alliancesApi = api.connect().eve.AllianceList()
            for a in alliancesApi.alliances:
                if a.allianceID == allianceID:
                    allianceTicker = a.shortName
                    break
        except eveapi.Error:
            LOG.exception("Failed to fetch AllianceList.xml.aspx from EVE API server")
            corp = Corp.objects.get(id=1)
            allianceID = corp.allianceID
            allianceName = corp.allianceName
            allianceTicker = corp.allianceTicker
    except:
        allianceName = "-"
        allianceID   = 0
        allianceTicker = "-"

    description = fix_description(corpApi.description)

    try:
        # try to retrieve the db stored corp info
        corp = Corp.objects.get(id=1)
        corp.corporationID   = corpApi.corporationID
        corp.corporationName = corpApi.corporationName
        corp.ticker          = corpApi.ticker
        corp.ceoID           = corpApi.ceoID
        corp.ceoName         = corpApi.ceoName
        corp.stationID       = corpApi.stationID
        corp.stationName     = corpApi.stationName
        corp.allianceID      = allianceID
        corp.allianceName    = allianceName
        corp.allianceTicker  = allianceTicker
        corp.description     = description
        corp.taxRate         = corpApi.taxRate
        corp.memberLimit     = corpApi.memberLimit
    except ObjectDoesNotExist:
        # no corp parsed yet
        corp = Corp( id              = 1,
                     corporationID   = corpApi.corporationID,
                     corporationName = corpApi.corporationName,
                     ticker          = corpApi.ticker,
                     ceoID           = corpApi.ceoID,
                     ceoName         = corpApi.ceoName,
                     stationID       = corpApi.stationID,
                     stationName     = corpApi.stationName,
                     description     = description,
                     allianceID      = allianceID,
                     allianceName    = allianceName,
                     allianceTicker  = allianceTicker,
                     taxRate         = corpApi.taxRate,
                     memberLimit     = corpApi.memberLimit )

    corp.save()
    # we store the update time of the table
    UpdateDate.mark_updated(model=Corp, date=currentTime)

    return corp


#------------------------------------------------------------------------------
def update_hangar_divisions(corpApi, currentTime):
    LOG.debug("HANGAR DIVISIONS:")
    for hangarDiv in corpApi.divisions:
        h_id = hangarDiv.accountKey
        h_name = hangarDiv.description
        try:
            h = Hangar.objects.get(hangarID=h_id)
            h.name = h_name
        except ObjectDoesNotExist:
            h = Hangar(hangarID=h_id, name=h_name)
        LOG.debug("  %s [%d]", h.name, h.hangarID)
        h.save()
    # we store the update time of the table
    UpdateDate.mark_updated(model=Hangar, date=currentTime)


#------------------------------------------------------------------------------
def update_wallet_divisions(corpApi, currentTime):
    LOG.debug("WALLET DIVISIONS:")
    for walletDiv in corpApi.walletDivisions:
        w_id = walletDiv.accountKey
        w_name = walletDiv.description
        try:
            w = Wallet.objects.get(walletID=w_id)
            w.name = w_name
        except ObjectDoesNotExist:
            w = Wallet(walletID=w_id, name=w_name)
        LOG.debug("  %s [%d]", w.name, w.walletID)
        w.save()
    # we store the update time of the table
    UpdateDate.mark_updated(model=Wallet, date=currentTime)

#------------------------------------------------------------------------------
FONT_TAG_REGEXP = re.compile('</?font.*?>', re.DOTALL)
SPAN_TAG_REGEXP = re.compile('</?span.*?>', re.DOTALL)
def fix_description(description):
    # an empty corp description string ('<description />' )will throw a TypeError
    # so let's catch it
    try:
        desc, _ = FONT_TAG_REGEXP.subn("", description)
        desc, _ = SPAN_TAG_REGEXP.subn("", desc)
        return desc.strip()
    except TypeError:
        return '-'

