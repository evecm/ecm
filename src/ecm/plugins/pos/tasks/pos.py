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

from ecm.core.eve.classes import Item
from ecm.plugins.pos.models import POS, FuelLevel
from ecm.plugins.pos import constants
from ecm.core.eve import api, db
from ecm.core.parsers import checkApiVersion

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
    try:
        conn = api.connect()
        charID = api.get_api().characterID

        logger.info("fetching /corp/StarbaseList.xml.aspx...")
        apiPOSList = conn.corp.StarbaseList(characterID=charID)
        checkApiVersion(apiPOSList._meta.version)

        newPOSes = 0
        updatedPOSes = 0
        oldPOSesIDs = list(POS.objects.all().values_list('itemID', flat=True))
        for row in apiPOSList.starbases:
            pos, created = POS.objects.get_or_create(itemID=row.itemID)
            if created:
                newPOSes += 1
            else:
                oldPOSesIDs.remove(row.itemID)
                updatedPOSes += 1
            fillFieldsFromListInfo(pos, row)

            logger.info("fetching /corp/StarbaseDetail.xml.aspx?itemID=%d..." % row.itemID)
            apiCurPOS = conn.corp.StarbaseDetail(characterID=charID,
                                                 itemID=row.itemID)
            cachedUntil = apiCurPOS._meta.cachedUntil

            if cachedUntil != pos.cachedUntil:
                pos.cachedUntil = cachedUntil
                fillFieldsFromDetailInfo(pos, apiCurPOS)
            else:
                localCachedUntil = datetime.fromtimestamp(calendar.timegm(cachedUntil.timetuple()))
                logger.info("POS %s is cached until %s: no update required",
                            row.itemID, localCachedUntil)
            pos.save()

        # if this list is not empty, it means that some POSes have disapeared since last scan.
        if len(oldPOSesIDs) > 0:
            POS.objects.filter(itemID__in=oldPOSesIDs).delete()

        logger.info("%d POS updated, %d new, %d removed", updatedPOSes, newPOSes, len(oldPOSesIDs))
    except:
        # error catched, rollback changes
        logger.exception("update failed")
        raise

#------------------------------------------------------------------------------
def fillFieldsFromListInfo(pos, apiRow):
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
    pos.itemID = apiRow.itemID
    pos.locationID = apiRow.locationID
    pos.moonID = apiRow.moonID
    pos.typeID = apiRow.typeID

    pos.location, _   = db.resolveLocationName(pos.locationID)
    pos.moon, _  = db.resolveLocationName(pos.moonID)

    i = Item.get(pos.typeID)
    pos.typeName = i.typeName
    pos.isotopeTypeID = constants.RACE_TO_ISOTOPE[i.raceID]

#------------------------------------------------------------------------------
def fillFieldsFromDetailInfo(pos, api):
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
    pos.stateTimestamp = api.stateTimestamp
    pos.onlineTimestamp = api.onlineTimestamp
    pos.lastUpdate = api._meta.currentTime

    gs = api.generalSettings
    pos.usageFlags = gs.usageFlags
    pos.deployFlags = gs.deployFlags
    pos.allowCorporationMembers = gs.allowCorporationMembers == 1
    pos.allowAllianceMembers = gs.allowAllianceMembers == 1

    cs = api.combatSettings
    pos.useStandingsFrom = cs.useStandingsFrom.ownerID
    pos.standingThreshold = cs.onStandingDrop.standing / 100.0
    pos.attackOnConcordFlag = cs.onStatusDrop.enabled == 1
    pos.securityStatusThreshold = cs.onStatusDrop.standing / 100.0
    pos.attackOnAggression = cs.onAggression.enabled == 1
    pos.attackOnCorpWar = cs.onCorporationWar.enabled == 1

    for fuel in api.fuel:
        try:
            previousLevel = pos.fuel_levels.filter(typeID=fuel.typeID).latest()
        except FuelLevel.DoesNotExist:
            previousLevel = None

        currentLevel = FuelLevel.objects.create(pos=pos,
                                                typeID=fuel.typeID,
                                                quantity=fuel.quantity,
                                                date=api._meta.currentTime)
        if previousLevel is not None:
            # cannot estimate consumption without a previous level
            updateFuelConsumption(pos, currentLevel, previousLevel)

#------------------------------------------------------------------------------
def updateFuelConsumption(pos, currentLevel, previousLevel):
    """
    This function estimates the fuel consumption based on previous and current fuel levels.

    The estimation involves 4 variables:
        consumption
            the quantity of fuel burned per hour
        stability
            the number of hours since when the consumption did not change
            it is resetted to 0 whenever the consumption changes
        probableConsumption
            if the consumption does not change for 24 hours
        probableStability
    """
    fuelCons, _ = pos.fuel_consumptions.get_or_create(typeID=currentLevel.typeID)

    levelDelta = previousLevel.quantity - currentLevel.quantity
    if levelDelta < 0:
        # particular case : refuel ... cannot estimate consumption
        return

    # time since previous level (must be in hours)
    timeDelta = (currentLevel.date - previousLevel.date).total_seconds() / 3600
    if timeDelta < 0:
        # if timeDelta is negative (time travel?) cannot estimate consumption
        return
    elif timeDelta < 1.0:
        # if timeDelta is less than 1 hour, make it 1 hour
        timeDelta = 1.0

    # quantity of fuel consumed per hour
    consumption = int(round(levelDelta / timeDelta))

    if fuelCons.consumption == consumption:
        # consumption didn't change since last scan,
        # we increase the "stability" of the consumption
        fuelCons.stability += timeDelta

        if fuelCons.stability >= fuelCons.probableStability or fuelCons.stability >= 24:
            # 24 hours with the same value we consider it stable.
            fuelCons.probableStability = fuelCons.stability
            fuelCons.probableConsumption = fuelCons.consumption
    else:
        # consumption changed since last scan
        if fuelCons.consumption == 0 and fuelCons.stability == 0:
            # initialization: no previous info about stability and stuff
            fuelCons.consumption = consumption
        else:
            if fuelCons.stability > 0:
                # consumption was stable until now, we do not take the new value into account.
                # instead we reset the stability to 0.
                # on next scan, if the consumption has not gone back to what it was before,
                # we will take it into account.
                fuelCons.stability = 0
            else:
                # stability was set to 0 at last scan because it had changed
                # we take the new consumption into account now as it is still different
                fuelCons.consumption = consumption

    fuelCons.save()

