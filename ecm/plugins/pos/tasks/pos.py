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
__author__ = "JerryKhan"

import logging
import calendar
from datetime import datetime

from django.db import transaction

from ecm.plugins.pos.models import POS, FuelLevel
from ecm.apps.eve.models import CelestialObject, ControlTowerResource, Type
from ecm.plugins.pos import constants
from ecm.apps.eve import api
from ecm.core.parsers import checkApiVersion
from ecm.apps.corp.models import Corp

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
    checkApiVersion(apiPOSList._meta.version)

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
        cached_until = apiCurPOS._meta.cachedUntil

        if cached_until != pos.cached_until:
            pos.cached_until = cached_until
            get_details(pos, apiCurPOS, sov)
        else:
            localCachedUntil = datetime.fromtimestamp(calendar.timegm(cached_until.timetuple()))
            logger.info("POS %s is cached until %s: no update required",
                        row.itemID, localCachedUntil)
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

    pos.location = CelestialObject.objects.get(itemID=pos.location_id).itemName
    pos.moon = CelestialObject.objects.get(itemID=pos.moon_id).itemName
    #pos.location, _   = db.resolveLocationName(pos.location_id) 
    #pos.moon, _  = db.resolveLocationName(pos.moon_id)

    item = Type.objects.get(pk=pos.type_id)
    pos.type_name = item.typeName
    pos.fuel_type_id = constants.RACE_TO_FUEL[item.raceID]

#------------------------------------------------------------------------------
def get_details(pos, api, sov):
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
    pos.state = api.state
    pos.state_timestamp = api.stateTimestamp
    pos.online_timestamp = api.onlineTimestamp
    pos.lastUpdate = api._meta.currentTime

    gs = api.generalSettings
    pos.usage_flags = gs.usageFlags
    pos.deploy_flags = gs.deployFlags
    pos.allow_corporation_members = gs.allowCorporationMembers == 1
    pos.allow_alliance_members = gs.allowAllianceMembers == 1

    cs = api.combatSettings
    pos.use_standings_from = cs.useStandingsFrom.ownerID
    pos.standings_threshold = cs.onStandingDrop.standing / 100.0
    pos.attack_on_concord_flag = cs.onStatusDrop.enabled == 1
    pos.security_status_threshold = cs.onStatusDrop.standing / 100.0
    pos.attack_on_aggression = cs.onAggression.enabled == 1
    pos.attack_on_corp_war = cs.onCorporationWar.enabled == 1

    for fuel in api.fuel:
        fuel_level = FuelLevel.objects.create(pos=pos,
                                     type_id = fuel.typeID,
                                     quantity = fuel.quantity,
                                     date = api._meta.currentTime)
        base_fuel_cons = ControlTowerResource.objects.get(control_tower=pos.type_id, resource=fuel.typeID).quantity
        #base_fuel_cons = db.getFuelConsumption(pos.type_id, fuel.typeID)
        corp = Corp.objects.latest()
        if sov[pos.location_id]['alliance'] == corp.allianceID and base_fuel_cons > 1:
            base_fuel_cons = int(round(base_fuel_cons * .75))
        fuel_level.consumption = base_fuel_cons
        fuel_level.save()
    
    #if db.getSecurityStatus(pos.location_id) > constants.CHARTER_MIN_SEC_STATUS:
    if CelestialObject.objects.get(itemID=pos.location_id).security > constants.CHARTER_MIN_SEC_STATUS:
        charters = constants.RACEID_TO_CHARTERID[sov[pos.location_id]['faction']]
        try:
            pos.fuel_levels.filter(type_id=charters).latest()
        except FuelLevel.DoesNotExist:
            fuel_level = FuelLevel.objects.create(pos = pos,
                                                 type_id = charters,
                                                 quantity = 0,
                                                 date = api._meta.currentTime)
            fuel_level.save()
    #for fuel in api.fuel:
        #try:
            #previous_level = pos.fuel_levels.filter(type_id=fuel.typeID).latest()
        #except FuelLevel.DoesNotExist:
            #previous_level = None

        #current_level = FuelLevel.objects.create(pos=pos,
        #                                         type_id=fuel.typeID,
        #                                         quantity=fuel.quantity,
        #                                         date=api._meta.currentTime)
        #if previous_level is not None:
            # cannot estimate consumption without a previous level
            #get_fuel_consumption(pos, current_level, previous_level)

#------------------------------------------------------------------------------
#def get_fuel_consumption(pos, current_level, previous_level):
"""
This function estimates the fuel consumption based on previous and current fuel levels.

The estimation involves 4 variables:
    consumption
        the quantity of fuel burned per hour
    stability
        the number of hours since when the consumption did not change
        it is resetted to 0 whenever the consumption changes
    probable_consumption
        if the consumption does not change for 24 hours
    probable_stability
"""
    #fuel_cons, _ = pos.fuel_consumptions.get_or_create(type_id=current_level.type_id)

    #level_delta = previous_level.quantity - current_level.quantity
    #if level_delta < 0:
        # particular case : refuel ... cannot estimate consumption
        #return

    # time since previous level (must be in hours)
    #time_delta = (current_level.date - previous_level.date).total_seconds() / 3600
    #if time_delta < 0:
        # if time_delta is negative (time travel?) cannot estimate consumption
        #return
    #elif time_delta < 1.0:
        # if time_delta is less than 1 hour, make it 1 hour
        #time_delta = 1.0

    # quantity of fuel consumed per hour
    #consumption = int(round(level_delta / time_delta))

    #if fuel_cons.consumption == consumption:
        # consumption didn't change since last scan,
        # we increase the "stability" of the consumption
        #fuel_cons.stability += time_delta

        #if fuel_cons.stability >= fuel_cons.probable_stability or fuel_cons.stability >= 24:
            # 24 hours with the same value we consider it stable.
            #fuel_cons.probable_stability = fuel_cons.stability
            #fuel_cons.probable_consumption = fuel_cons.consumption
    #else:
        # consumption changed since last scan
        #if fuel_cons.consumption == 0 and fuel_cons.stability == 0:
            # initialization: no previous info about stability and stuff
            #fuel_cons.consumption = consumption
        #else:
            #if fuel_cons.stability > 0:
                # consumption was stable until now, we do not take the new value into account.
                # instead we reset the stability to 0.
                # on next scan, if the consumption has not gone back to what it was before,
                # we will take it into account.
                #fuel_cons.stability = 0
            #else:
                # stability was set to 0 at last scan because it had changed
                # we take the new consumption into account now as it is still different
                #fuel_cons.consumption = consumption

    #fuel_cons.save()
