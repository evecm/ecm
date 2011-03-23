'''
This file is part of EVE Corporation Management

Created on 23 mar. 2010
@author: diabeteman
'''
from ecm.lib import eveapi
from ecm.data.api.models import APIKey
from ecm.core.api.cache import CacheHandler
from django.core.exceptions import ObjectDoesNotExist

def get_api():
    try:
        return APIKey.objects.all().order_by("-id")[0]
    except IndexError:
        raise ObjectDoesNotExist("There is no APIKey registered in the database")

def set_api(api_new):
    try:
        api = APIKey.objects.all().order_by("-id")[0]
    except IndexError:
        api = APIKey()
    api.name = api_new.name
    api.userID = api_new.userID
    api.charID = api_new.charID
    api.key = api_new.key
    api.save()

def connect(proxy=None, cache=False):
    if cache : handler = CacheHandler()
    else     : handler = None
    conn = eveapi.EVEAPIConnection(cacheHandler=handler, proxy=proxy)
    api = get_api()
    return conn.auth(userID=api.userID, apiKey=api.key)
