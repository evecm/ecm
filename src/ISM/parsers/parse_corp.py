'''
This file is part of ICE Security Management

Created on 8 feb. 2010
@author: diabeteman
'''

import xml.dom.minidom
from xml.dom.minidom import Node

from ISM.corp.models import Hangar, Wallet, Corp
from ISM.parsers.parse_utils import checkApiVersion, getText, getNode, reachRowset

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

#______________________________________________________________________________
@transaction.commit_manually
def parse(xmlFile):
    """
    Parses all Corporation information from an API CorporationSheet.xml response.
    Puts all the information into the database.
       
       @param xmlFile: can be either a string or a physical file.
       
    """
    try:
        doc = xml.dom.minidom.parse(xmlFile)
        checkApiVersion(doc)
        result = getNode(doc, "result")
        
        id        = int(getText(getNode(result, "corporationID")))
        name      =     getText(getNode(result, "corporationName"))
        tick      =     getText(getNode(result, "ticker"))
        ceo       = int(getText(getNode(result, "ceoID")))
        hq        = int(getText(getNode(result, "stationID")))
        alliance  =     getText(getNode(result, "allianceName"))
        tax       = int(getText(getNode(result, "taxRate")))
        memberLim =     getText(getNode(result, "memberLimit"))

        try:
            corp = Corp.objects.get(corporationID=id)
            corp.corporationName = name
            corp.ticker          = tick
            corp.ceoID           = ceo
            corp.stationID       = hq
            corp.allianceName    = alliance
            corp.taxRate         = tax
            corp.memberLimit     = memberLim
            corp.save()
        except ObjectDoesNotExist:
            Corp( corporationID=id, corporationName=name,
                  ticker=tick,      ceoID=ceo,
                  stationID=hq,     allianceName=alliance,
                  taxRate=tax,      memberLimit=memberLim ).save()

        hangars = reachRowset(result, "divisions")
        for h in hangars.childNodes :
            if not h.nodeType == Node.ELEMENT_NODE:
                continue
            h_id = h.getAttribute("accountKey")
            h_name = h.getAttribute("description")
            try:
                hangar = Hangar.objects.get(hangarID=h_id)
                if not hangar.name == h_name:
                    hangar.name = h_name
                    hangar.save()
            except ObjectDoesNotExist: 
                Hangar(hangarID=h_id, name=h_name).save()
        
        
        wallets = reachRowset(result, "walletDivisions")
        for w in wallets.childNodes :
            if not w.nodeType == Node.ELEMENT_NODE:
                continue
            w_id = w.getAttribute("accountKey")
            w_name = w.getAttribute("description")
            try:
                wallet = Wallet.objects.get(walletID=w_id)
                if not wallet.name == w_name:
                    wallet.name = w_name
                    wallet.save()
            except ObjectDoesNotExist: 
                Wallet(walletID=w_id, name=w_name).save()
        
        transaction.commit()
    except:
        transaction.rollback()
        raise
