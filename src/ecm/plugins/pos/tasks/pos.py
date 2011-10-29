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

from ecm.data.pos.models import POS,FuelLevel,FUELCOMPOS # TODO database POS
from ecm.core.eve import api,db,constants
from ecm.core.parsers import checkApiVersion    
from django.db import transaction
import logging
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_manually
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
        logger.info("fetching /corp/StarbaseList.xml.aspx...")
        api_conn = api.connect()
        apiPos = api_conn.corp.StarbaseList(characterID=api.get_api().characterID)
        checkApiVersion(apiPos._meta.version)
        
        currentTime = apiPos._meta.currentTime
        logger.debug("current time : %s", str(currentTime)) # In fact current time ahs no real added value (at the contrary of Cached Time)
        logger.debug("cached  time : %s", str(apiPos._meta.cachedUntil))
        logger.info("parsing api response...")
        
        # I dont want to store stupidely information if no changes occures.
        # I store the cache and if cache date = current cache date ... Ignore update. 
        
        for row in apiPos.starbases :
            try:    pos = POS.objects.get(itemID=row.itemID)    # Get the POS instance to update or ..
            except: pos = POS()                                 # create DB instance
            fillFieldsFromListInfo(pos,row)                     # first filling (No cachedUnitl constraint
            apiCurPos = api_conn.corp.StarbaseDetail(characterID=api.get_api().characterID, itemID=row.itemID)
            cachedUntil = apiCurPos._meta.cachedUntil
            
            if cachedUntil != pos.cachedUntil:
                logger.info("POS %s : State %s at %s, Online at %s Cached: %s", row.itemID, apiCurPos.state, apiCurPos.stateTimestamp, apiCurPos.onlineTimestamp, cachedUntil)
                pos.cachedUntil = cachedUntil
                fillFieldsFromEveDB(pos,row.itemID)
                try: fillFieldsFromDetailInfo(pos,apiCurPos) # second filling.
                except Exception,msg: 
                    pass
            else:
                logger.info("POS %s : Cached: %s ... No Update required", row.itemID, cachedUntil)
            pos.save()
            
        logger.info("%d POS parsed", len(apiPos.starbases))
        logger.debug("saving to database...")
        transaction.commit()
        logger.debug("DATABASE UPDATED!")
    except:
        # error catched, rollback changes
        transaction.rollback()
        logger.exception("update failed")
        raise
    
#____________________
def fillFieldsFromEveDB(pos, id):
    #pos.typeName = db.resolveTypeNames(id)
    pos.typeName = id
    #lastWord = pos.typeName.split()[-1]      # the size of a POS is usefull to evaluate consumption.
    #if lastWord == 'Small': pos.size = 1
    #elif lastWord == 'Medium' : pos.size = 2
    #else : pos.size = 3
    
#____________________
def fillFieldsFromListInfo(pos, apiRow):
        ''' The XML API result of StarbaseList is 
<eveapi version="2"><currentTime>2011-04-24 00:24:31</currentTime><result>
<rowset name="starbases" key="itemID" columns="itemID,typeID,locationID,moonID,state,stateTimestamp,onlineTimestamp,standingOwnerID">
<row itemID="1001853458191" typeID="16213" locationID="30002924" moonID="40185540" state="4" stateTimestamp="2011-04-24 01:15:55" onlineTimestamp="2011-04-02 08:14:47" standingOwnerID="1354830081"/>
[...]
</rowset></result><cachedUntil>2011-04-24 06:21:31</cachedUntil></eveapi>
        '''
        for f in ['itemID','locationID','moonID','typeID','standingOwnerID']:
            setattr(pos, f, getattr(apiRow, f))
        pos.location   = db.resolveLocationName(pos.locationID)[0]
        pos.mlocation, security  = db.resolveLocationName(pos.moonID)
#____________________    
def fillFieldsFromDetailInfo(pos, apiResult):
    '''The XML API result of StarbaseDetail is 
<eveapi version="2"><currentTime>2011-04-24 00:24:31</currentTime><result>
    <state>4</state>                                            # already in starbaseList, but we use this
    <stateTimestamp>2011-04-24 01:15:55</stateTimestamp>        # already in starbaseList, but we use this
    <onlineTimestamp>2011-04-02 08:14:47</onlineTimestamp>      # already in starbaseList, but we use this
    <generalSettings>
        <usageFlags>3</usageFlags>
        <deployFlags>0</deployFlags>
        <allowCorporationMembers>1</allowCorporationMembers>
        <allowAllianceMembers>1</allowAllianceMembers>
    </generalSettings>
    <combatSettings>
        <useStandingsFrom ownerID="1354830081"/>                # already in starbaseList, we stored it
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
    </rowset></result><cachedUntil>2011-04-24 01:21:31</cachedUntil></eveapi>
        '''
    for f in ['state','stateTimestamp','onlineTimestamp']:
        setattr(pos, f, getattr(apiResult, f))
    for f in ['usageFlags','deployFlags','allowCorporationMembers','allowAllianceMembers']:
        setattr(pos, f, getattr(apiResult.generalSettings, f))
    pos.onStandingDropStanding = apiResult.combatSettings.onStandingDrop.standing
    pos.onStatusDropEnabled = apiResult.combatSettings.onStatusDrop.enabled
    pos.onStatusDropStanding = apiResult.combatSettings.onStatusDrop.standing
    pos.onAggressionEnabled = apiResult.combatSettings.onAggression.enabled
    pos.onCorporationWarEnabled = apiResult.combatSettings.onCorporationWar.enabled
    for f in apiResult.fuel:
        if f.typeID in constants.ID_ISOTOPS:
            pos.isotope = constants.ISOTOPS_ICONS[f.typeID]
            break
    for f in apiResult.fuel:
        # fill the FuelLevel table with data. 
        try:    latestFL = pos.fuel_levels.filter(typeID=f.typeID).latest()
        except: latestFL=None
        curFL = FuelLevel.objects.create(pos=pos, typeID=f.typeID
                                         , quantity=f.quantity
                                         , date=apiResult._meta.currentTime)
        fillFuelConsumption(pos, curFL, latestFL, apiResult)
        curFL.save()
#____________________
def fillFuelConsumption(pos, curFL, latestFL, apiResult):
    '''The principle consists in getting the last information on fuel content to evaluate the hourly consumption
    This value should be an estimation of the consumption to show number of hours before empty fuel
    I added a resistance to change with probable concept to avoid taking into account dirac changes.
    
    in case of no info : the display return 0 means N/A
    in case of only one info: the display return 0 N/A
    in case of 2 only: the consumption has the difference
    a,b  => a-b    S=0 PC=a-b PS=0
    a,b,c => b-c  if equal S+=1 PS<S => PS=S and PC=C (on additional stability point)
             b-c  if different S=0 PC,PS not changed (No stability risk to fail)
    
    real sequence: 
    12--->3 hours--->9 -> delta (C) = 1 stab (S) +=3
    
    4,4,4,5,4,4 : Sequence of delta between 2 last info (related to hours)
    :             C=0 S=0 PC=0 PS=0   initial state (NO FC created !)
    4:            C=4 S=1 PC=4 PS=1   first value PS<S => update PS and PC
    4,4:          C=4 S=2 PC=4 PS=2   PS<=S => update PS and PC
    4,4,4:        C=4 S=3 PC=4 PS=3   PS<=S => update PS and PC
    4,4,4,5:      C=5 S=0 PC=4 PS=3   C different PC PS not changed PS>0
    4,4,4,5,4:    C=4 S=0 PC=4 PS=3   C different PC PS not changed PS>0
    4,4,4,5,4,4:  C=4 S=1 PC=4 PS=3   PS >= S(1) then no change on PS and PC
    
    4,4,5,5,5:
    4,4,5:        C=5 S=0 PC=4 PS=2   C different PC PS not changed PS>0
    4,4,5,5:      C=5 S=1 PC=4 PS=2   PS >= S and S<48 => No change
       We can considere that the same value during 2 days is a stable value.
       to reinitialise the PS counter.
    4,4,5,5,5:    C=5 S=2 PC=5 PS=2   PS <= S => update PC,PS 
    
    # Copy/Past these 2 functions in the python IDLE to validate the algorithm:
    
    # D is the current Fuel Delta consumption, DT is the number of hours between previous capture
    # MT is the number of hours we consider the value probably stable.
    def test(D,DT,MT,C,S,PC,PS):
        if C == D:
            S += DT
            if S >= PS or S >=MT: PS = S; PC = C
        else:
            if C == 0 and S == 0: C = D
            else:
                if S == 0: C = D
                else: S = 0
        return C,S,PC,PS
    # SEQ is the sequence of captures in terme of delta.
    def seq(SEQ,DT=None,MT=None,FT=None):
        C,S,PC,PS = 0,0,0,0
        if FT is None: FT = 1
        if DT is None: DT = [FT,]*len(SEQ)
        if MT is None: MT = 24
        print "C:",C,"S:",S,"PC:",PC,"PS:",PS
        for i,v in enumerate(SEQ):
            C,S,PC,PS = test(v,DT[i],MT,C,S,PC,PS)
            print "i:",i,"D=",v,"DT:",DT[i],"C:",C,"S:",S,"PC:",PC,"PS:",PS
            
    seq([6,3,3,3,3,3,3,3,3,3,4,3,3,3,3,3,3,3,3,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10],MT=5)
    '''  
    curFC, bool = pos.fuel_consumptions.get_or_create(typeID=curFL.typeID)
        
    # Put in place the algorithm 1 get the information
    # get the previous FL to gather the delta 
    #latestFL = pos.fuel_levels.filter(typeID=curFL.typeID).latest()
    #if not latestFL: return   # special case (near initialisation no FC created wait for already existing FL) 
    deltaC = latestFL.quantity - curFL.quantity           # diff of fuel compo
    deltadT = (curFL.date - latestFL.date)
    deltaT= deltadT.seconds / 3600  # diff of time (must be in hours)
    
    # particular case : refuel ... we ignore completely the process
    if deltaC < 0: return
    
    # patricular case : deltaC == 0
    if not deltaC: 
        delta = 0
    else:
        if deltaT < 1: # case if too small time interval ..|...^..|..^..|
            deltaT = 1
        delta = int(round(deltaC/deltaT))
    
    # make the algorithm
    if curFC.consumption == delta:
        curFC.stability += deltaT
        if curFC.stability >= curFC.probableStability or curFC.stability >= 24: # 24 hours with the same value we consider it stable.
            curFC.probableStability = curFC.stability
            curFC.probableConsumption = curFC.consumption
        else : pass # no change.
    else:
        if curFC.consumption == 0 and curFC.stability == 0:  # Initialisation 
            curFC.consumption = delta
        else: 
            if curFC.stability == 0:
                curFC.consumption = delta
            else:
                curFC.stability = 0
                
    curFC.save()
