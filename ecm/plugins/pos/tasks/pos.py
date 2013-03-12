# Copyright (c) 2011 jerome Vacher
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

__date__ = "2010 04 23"
__author__ = "Ajurna"

import logging

from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext as tr

from ecm.plugins.pos.models import POS, FuelLevel
from ecm.apps.eve.models import CelestialObject, ControlTowerResource, Type
from ecm.plugins.pos import constants
from ecm.apps.common import api
from ecm.apps.corp.models import Corporation

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update():
    """
    Retrieve all POS informations
    First : get the POS list using StarbaseList
    Then : retreive information of each of them using StarbaseDetails
    And update the database.

    If there's an error, nothing is written in the database
    If the cache date didnot change ...ignore...
    """
    conn = api.connect()
    charID = api.get_charID()

    logger.info("fetching /corp/StarbaseList.xml.aspx...")
    apiPOSList = conn.corp.StarbaseList(characterID=charID)
    api.check_version(apiPOSList._meta.version)

    newPOSes = 0
    updatedPOSes = 0
    sov = get_sov_info(conn.map.Sovereignty().solarSystems)
    oldPOSesIDs = list(POS.objects.all().values_list('item_id', flat=True))
    for row in apiPOSList.starbases:
        pos, created = POS.objects.get_or_create(item_id=row.itemID)
        if created:
            newPOSes += 1
        else:
            oldPOSesIDs.remove(row.itemID)
            updatedPOSes += 1
        get_basic_info(pos, row)

        logger.info("fetching /corp/StarbaseDetail.xml.aspx?itemID=%d..." % row.itemID)
        apiCurPOS = conn.corp.StarbaseDetail(characterID=charID,
                                             itemID=row.itemID)
        
        
        cached_until = timezone.make_aware(apiCurPOS._meta.cachedUntil, timezone.utc)
        if cached_until != pos.cached_until:
            pos.cached_until = cached_until
            get_details(pos, apiCurPOS, sov)
        else:
            logger.info("POS %s is cached until %s: no update required",
                        row.itemID, pos.cached_until)
        pos.save()

    # if this list is not empty, it means that some POSes have disapeared since last scan.
    if len(oldPOSesIDs) > 0:
        POS.objects.filter(item_id__in=oldPOSesIDs).delete()

    logger.info("%d POS updated, %d new, %d removed", updatedPOSes, newPOSes, len(oldPOSesIDs))

#------------------------------------------------------------------------------
def get_sov_info(systems):
    """
    convert the sovernty rowset to a dict.
    sov[systemID] = {}
    sov[systemID]['faction'] = 0#int
    sov[systemID]['alliance'] = 0#int
    """
    sov = {}
    for system in systems:
        sov[system.solarSystemID] = {}
        sov[system.solarSystemID]['faction'] = system.factionID
        sov[system.solarSystemID]['alliance'] = system.allianceID
    return sov

#------------------------------------------------------------------------------
def get_basic_info(pos, api_row):
    """
    The XML API result of StarbaseList is

    <eveapi version="2">
        <currentTime>2011-04-24 00:24:31</currentTime>
        <result>
            <rowset name="starbases" key="itemID"
                    columns="itemID,typeID,locationID,moonID,state,...">
                <row itemID="1001853458191"
                     typeID="16213"
                     locationID="30002924"
                     moonID="40185540"
                     state="4"
                     stateTimestamp="2011-04-24 01:15:55"
                     onlineTimestamp="2011-04-02 08:14:47"
                     standingOwnerID="1354830081"/>
                [...]
            </rowset>
        </result>
        <cachedUntil>2011-04-24 06:21:31</cachedUntil>
    </eveapi>
    """
    pos.item_id = api_row.itemID
    pos.location_id = api_row.locationID
    pos.moon_id = api_row.moonID
    pos.type_id = api_row.typeID
    pos.state = api_row.state

    pos.location = CelestialObject.objects.get(itemID=pos.location_id).itemName
    if pos.state != 0: #unanchored
        pos.moon = CelestialObject.objects.get(itemID=pos.moon_id).itemName
    else:
        pos.moon = tr('unanchored')

    item = Type.objects.get(pk=pos.type_id)
    pos.type_name = item.typeName
    pos.fuel_type_id = constants.RACE_TO_FUEL[item.raceID]

#------------------------------------------------------------------------------
def get_details(pos, api_resp, sov):
    """
    The XML API result of StarbaseDetail is

    <eveapi version="2">
        <currentTime>2011-04-24 00:24:31</currentTime>
        <result>
            <state>4</state>
            <stateTimestamp>2011-04-24 01:15:55</stateTimestamp>
            <onlineTimestamp>2011-04-02 08:14:47</onlineTimestamp>
            <generalSettings>
                <usageFlags>3</usageFlags>
                <deployFlags>0</deployFlags>
                <allowCorporationMembers>1</allowCorporationMembers>
                <allowAllianceMembers>1</allowAllianceMembers>
            </generalSettings>
            <combatSettings>
                <useStandingsFrom ownerID="1354830081"/>
                <onStandingDrop standing="10"/>
                <onStatusDrop enabled="0" standing="0"/>
                <onAggression enabled="0"/>
                <onCorporationWar enabled="1"/>
            </combatSettings>
            <rowset name="fuel" key="typeID" columns="typeID,quantity">
                <row typeID="44" quantity="1125"/>
                <row typeID="3683" quantity="6901"/>
                <row typeID="3689" quantity="1276"/>
                <row typeID="9832" quantity="2250"/>
                <row typeID="9848" quantity="151"/>
                <row typeID="16273" quantity="53414"/>
                <row typeID="16272" quantity="51127"/>
                <row typeID="17888" quantity="73691"/>
                <row typeID="16275" quantity="8000"/>
            </rowset>
        </result>
        <cachedUntil>2011-04-24 01:21:31</cachedUntil>
    </eveapi>
    """
    current_time = timezone.make_aware(api_resp._meta.currentTime, timezone.utc)
    
    pos.state = api_resp.state
    pos.state_timestamp = timezone.make_aware(api_resp.stateTimestamp, timezone.utc)
    pos.online_timestamp = timezone.make_aware(api_resp.onlineTimestamp, timezone.utc)
    pos.lastUpdate = current_time

    gs = api_resp.generalSettings
    pos.usage_flags = gs.usageFlags
    pos.deploy_flags = gs.deployFlags
    pos.allow_corporation_members = gs.allowCorporationMembers == 1
    pos.allow_alliance_members = gs.allowAllianceMembers == 1

    cs = api_resp.combatSettings
    pos.use_standings_from = cs.useStandingsFrom.ownerID
    pos.standings_threshold = float(cs.onStandingDrop.standing) / 100.0
    pos.attack_on_concord_flag = cs.onStatusDrop.enabled == 1
    pos.security_status_threshold = float(cs.onStatusDrop.standing) / 100.0
    pos.attack_on_aggression = cs.onAggression.enabled == 1
    pos.attack_on_corp_war = cs.onCorporationWar.enabled == 1

    for fuel in api_resp.fuel:
        fuel_level = FuelLevel.objects.create(pos=pos,
                                     type_id = fuel.typeID,
                                     quantity = fuel.quantity,
                                     date = current_time)

        base_fuel_cons = ControlTowerResource.objects.get(control_tower=pos.type_id, resource=fuel.typeID).quantity
        corp = Corporation.objects.mine()
        # sov fuel check
        try:
            if pos.location_id < 31000000:#check not in wh
                if sov[pos.location_id]['faction'] == 0 and \
                   sov[pos.location_id]['alliance'] == corp.alliance.allianceID and \
                   base_fuel_cons > 1:
                    base_fuel_cons = int(round(base_fuel_cons * .75))
        except AttributeError:
            pass
        fuel_level.consumption = base_fuel_cons
        fuel_level.save()

    if CelestialObject.objects.get(itemID=pos.location_id).security > constants.CHARTER_MIN_SEC_STATUS:
        charters = constants.RACEID_TO_CHARTERID[sov[pos.location_id]['faction']]
        try:
            pos.fuel_levels.filter(type_id=charters).latest()
        except FuelLevel.DoesNotExist:
            fuel_level = FuelLevel.objects.create(pos = pos,
                                                 type_id = charters,
                                                 quantity = 0,
                                                 consumption = 1,
                                                 date = current_time)
            fuel_level.save()
