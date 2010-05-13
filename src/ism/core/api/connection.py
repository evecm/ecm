'''
This file is part of ICE Security Management

Created on 23 mar. 2010
@author: diabeteman
'''
from ism.lib import eveapi
from ism.data.api.models import APIKey
from ism.core.api.cache import CacheHandler

class API:
    USER_ID = None
    API_KEY = None
    CHAR_ID = None

for a in APIKey.objects.all():
    API.USER_ID = a.userID
    API.CHAR_ID = a.charID
    API.API_KEY = a.key
    break

def connect(debug=False,proxy =None):
    api = eveapi.EVEAPIConnection(cacheHandler=CacheHandler(debug=debug), proxy=proxy)
    return api.auth(userID=API.USER_ID, apiKey=API.API_KEY)
    
