'''
This file is part of ICE Security Management

Created on 8 feb. 2010
@author: diabeteman
'''
from ism.data.corp.models import Corp, Hangar, Wallet
from ism.core.api import connection
from ism.core.api.connection import API

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from ism.core.parsers.utils import checkApiVersion, markUpdated

DEBUG = False # DEBUG mode

#------------------------------------------------------------------------------
@transaction.commit_manually
def update(debug=False, cache=False):
    """
    Fetch a /corp/CorporationSheet.xml.aspx api response, parse it and store it to 
    the database.
    """
    global DEBUG
    DEBUG = debug
    
    try:
        # connect to eve API
        api = connection.connect(debug=debug, cache=cache)
        # retrieve /corp/CorporationSheet.xml.aspx
        corpApi = api.corp.CorporationSheet(characterID=API.CHAR_ID)
        checkApiVersion(corpApi._meta.version)

        currentTime = corpApi._meta.currentTime
        cachedUntil = corpApi._meta.cachedUntil
        if DEBUG : print "current time : %s" % str(currentTime)
        if DEBUG : print "cached util  : %s" % str(cachedUntil)

        if DEBUG : print "parsing api response..."
        try:
            # try to retrieve the db stored corp info
            corp = Corp.objects.get(corporationID=corpApi.corporationID)
            corp.corporationName  = corpApi.corporationName
            corp.ticker           = corpApi.ticker
            corp.ceoID            = corpApi.ceoID
            corp.stationID        = corpApi.stationID
            try: 
                corp.allianceName = corpApi.allianceName
            except:
                corp.allianceName = ""
            corp.taxRate          = corpApi.taxRate
            corp.memberLimit      = corpApi.memberLimit
            corp.save()
            
        except ObjectDoesNotExist:
            # no corp parsed yet
            corp = Corp( corporationID   = corpApi.corporationID, 
                         corporationName = corpApi.corporationName,
                         ticker          = corpApi.ticker,      
                         ceoID           = corpApi.ceoID,
                         stationID       = corpApi.stationID,     
                         allianceName    = corpApi.allianceName,
                         taxRate         = corpApi.taxRate,      
                         memberLimit     = corpApi.memberLimit )
            corp.save()
        
        # we store the update time of the table
        markUpdated(model=Corp, date=currentTime)
        
        if DEBUG: 
            print "==============="
            print "= CORPORATION ="
            print "==============="
            print "name: %s [%s]" % (corp.corporationName, corp.ticker)
            print "alliance: %s" % corp.allianceName
            print "CEO: %s" % corpApi.ceoName
            print "tax rate: %d%%" % corp.taxRate
            print "member limit: %d" % corp.memberLimit
            
        if DEBUG: print "HANGAR DIVISIONS:"
        for hangarDiv in corpApi.divisions :
            h_id   = hangarDiv.accountKey
            h_name = hangarDiv.description
            try:
                hangar = Hangar.objects.get(hangarID=h_id)
                if not hangar.name == h_name:
                    hangar.name = h_name
                    hangar.save()
                    if DEBUG: print "*  %s" % hangar.name
                else: 
                    if DEBUG: print "   %s" % hangar.name
            except ObjectDoesNotExist: 
                Hangar(hangarID=h_id, name=h_name).save()
        
        # we store the update time of the table
        markUpdated(model=Hangar, date=currentTime)
        
        if DEBUG: print "WALLET DIVISIONS:"
        for walletDiv in corpApi.walletDivisions :
            w_id   = walletDiv.accountKey
            w_name = walletDiv.description
            try:
                wallet = Wallet.objects.get(walletID=w_id)
                if not wallet.name == w_name:
                    wallet.name = w_name
                    wallet.save()
                    if DEBUG: print "*  %s" % wallet.name
                else: 
                    if DEBUG: print "   %s" % wallet.name
            except ObjectDoesNotExist: 
                Wallet(walletID=w_id, name=w_name).save()
        
        # we store the update time of the table
        markUpdated(model=Wallet, date=currentTime)
        
        # all ok
        if DEBUG : print "saving data to the database..."
        transaction.commit()
        if DEBUG: print "DATABASE UPDATED!"

        return "corp info parsed"
    except:
        # error catched, rollback changes
        transaction.rollback()
        raise
