'''
This file is part of ICE Security Management

Created on 23 mar. 2010
@author: diabeteman
'''
from ISM.lib import eveapi
from ISM.api.models import APIKey


CACHE_HANDLER, PROXY, USER_ID, API_KEY, CHAR_ID = None

for a in APIKey.objects.all():
    USER_ID = a.userID
    CHAR_ID = a.charID
    API_KEY = a.apiKey
    break

def connect():
    api = eveapi.EVEAPIConnection(cacheHandler=CACHE_HANDLER, proxy=PROXY)
    return api.auth(userID=USER_ID, apiKey=API_KEY)
    