'''
This file is part of ICE Security Management

Created on 23 mar. 2010
@author: diabeteman
'''


from ISM.api import connection
from ISM.api.connection import CHAR_ID
from ISM.assets.models import DbAsset

from django.db import transaction

def fetchAndParse():
    
    api = connection.connect()
    apiAssets = api.corp.AssetList(characterID=CHAR_ID)
    
    # TODO : 
    