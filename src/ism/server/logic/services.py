'''
This file is part of ICE Security Management

Created on 12 apr. 2010
@author: diabeteman
'''
from ism.server.data.roles.models import MemberDiff

class CorpService():

    def getCorpArrivals(self):
        memberdiff = MemberDiff.objects.filter()
        
        

        arrivals = []
        arrivals.append("Diabeteman")
        return [(member.arrival, member.name) for member in arrivals]

    def getCorpDepartures(self):
        pass

    def getLastTitlesChanges(self):
        pass
    
class Member:
    
    pass