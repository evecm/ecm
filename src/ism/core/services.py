'''
This file is part of ICE Security Management

Created on 12 apr. 2010
@author: diabeteman
'''

import datetime

class CorpService():

    def getCorpArrivals(self):

        diab = MemberExample()
        diab.name = "Diabeteman"
        diab.arrivalDate += datetime.timedelta(days=-3)

        zum = MemberExample()
        zum.name = "Zumbala"
        zum.arrivalDate += datetime.timedelta(days=-2)

        members = []
        members.append(diab)
        members.append(zum)
        
        return members

    def getCorpDepartures(self):
        pass

    def getLastTitlesChanges(self):
        pass


class MemberExample():

    name = ""
    arrivalDate = datetime.date.today()
