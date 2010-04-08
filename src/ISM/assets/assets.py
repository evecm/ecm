'''
This file is part of ICE Security Management

Created on 18 mar. 2010
@author: diabeteman
'''

from ISM.assets import db
from ISM.assets.models import DbAsset

#------------------------------------------------------------------------------
class Item(object):
    
    def __init__(self, itemID, typeID, quantity, singleton):
        self.itemID = itemID
        self.typeID = typeID
        self.quantity = quantity
        self.assembled = singleton
        
    def __getattr__(self, attrName):
        if attrName == 'name' :
            if not self.name :
                self.name = db.resolveTypeName(self.typeID)
            return self.name
        else : 
            message = "'%s' object has no attribute '%s'" % (self.__class__.__name__, attrName)
            raise AttributeError(message=message)
     
#------------------------------------------------------------------------------
class Container(Item):

    def __init__(self, contents=[]):
        self.contents = contents
    
#------------------------------------------------------------------------------
class Ship(Container):
    
    def __init__(self, contents=[]):
        self.contents = contents
        
#------------------------------------------------------------------------------
class Hangar(object):
    
    def __init__(self, id, name, contents=[]):
        self.id = id
        self.contents = contents


#------------------------------------------------------------------------------
class Deliveries(object):
    
    def __init__(self, contents=[]):
        self.contents = contents
        
#------------------------------------------------------------------------------
class Office(object):
    
    def __init__(self, locationID):
        self.locationID = locationID
        
    def __getattr__(self, attrName):
        if attrName == 'name' :
            if not self.name :
                self.name = db.resolveStationName(self.locationID)
            return self.name
        else : 
            message = "'%s' object has no attribute '%s'" % (self.__class__.__name__, attrName)
            raise AttributeError(message=message)
        
#------------------------------------------------------------------------------
class CorpAssets(object):
    
    def __init__(self):
        pass
    
    def reset(self):
        if self.offices: del self.offices
        
    def __resolveOffices__(self):
        locIDs = DbAsset.objects.values('locationID').distinct()
        self.offices = [ Office(id) for id in locIDs ]
        return self.offices

    def __getattr__(self, attrName):
        if attrName == 'offices' :
            if not self.offices :
                self.__resolveOffices__()
            return self.offices
        else : 
            message = "'%s' object has no attribute '%s'" % (self.__class__.__name__, attrName)
            raise AttributeError(message=message)
       
       
       
       
        