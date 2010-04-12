'''
This file is part of ICE Security Management

Created on 23 mar. 2010
@author: diabeteman
'''


from ism.server.data.assets.models import DbAsset
from ism.server.logic.api import connection
from ism.server.logic.api.connection import API
from django.db import transaction

DEBUG = False # DEBUG mode

#------------------------------------------------------------------------------
@transaction.commit_manually
def update(debug=False):
    """
    Retrieve all corp assets and calculate the changes.
    
    If there's an error, nothing is written in the database
    """
    global DEBUG
    DEBUG = debug
    
    try:
        api = connection.connect()
        apiAssets = api.corp.AssetList(characterID=API.CHAR_ID)
        
        transaction.commit()
        if DEBUG: print "DATABASE UPDATED!"
    except:
        transaction.rollback()
        raise