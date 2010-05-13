'''
This file is part of ICE Security Management

Created on 12 avr. 2010
@author: diabeteman
'''

from ism.core.services import CorpService
from django.pimentech.network import JSONRPCService, jsonremote

service = JSONRPCService()

@jsonremote(service)
def getCorpArrivals(request):
    return CorpService.getCorpArrivals()

def getCorpDepartures(request):
    return CorpService.getCorpDepartures()

def getLastTitlesChanges(request):
    return CorpService.getLastTitlesChanges()