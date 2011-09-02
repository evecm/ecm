# Copyright (c) 2010-2011 Robin Jarry
# 
# This file is part of EVE Corporation Management.
# 
# EVE Corporation Management is free software: you can redistribute it and/or 
# modify it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or (at your 
# option) any later version.
# 
# EVE Corporation Management is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
# more details.
# 
# You should have received a copy of the GNU General Public License along with 
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

__date__ = "2010-03-23"
__author__ = "diabeteman"

import cPickle, os, tempfile, time, zlib
from datetime import datetime

from django.conf import settings

from ecm.lib import eveapi
from ecm.core.eve.validators import check_user_access_mask
from ecm.data.common.models import APIKey
from ecm.data.corp.models import Corp



#------------------------------------------------------------------------------
def get_api():
    try:
        return APIKey.objects.latest()
    except APIKey.DoesNotExist:
        raise APIKey.DoesNotExist("There is no APIKey registered in the database")

#------------------------------------------------------------------------------
def set_api(api_new):
    try:
        api = APIKey.objects.latest()
    except APIKey.DoesNotExist:
        api = APIKey()
    api.name = api_new.name
    api.keyID = api_new.keyID
    api.characterID = api_new.characterID
    api.vCode = api_new.vCode
    api.save()

#------------------------------------------------------------------------------
def connect(proxy=None, cache=False):
    """
    Creates a connection to the web API with director credentials 
    """
    if cache : handler = CacheHandler()
    else     : handler = None
    conn = eveapi.EVEAPIConnection(scheme="https", cacheHandler=handler, proxy=proxy)
    api = get_api()
    return conn.auth(keyID=api.keyID, vCode=api.vCode)

#------------------------------------------------------------------------------
def connect_user(user_api, proxy=None, cache=False):
    """
    Creates a connection to the web API with a user's credentials
    """
    if cache : handler = CacheHandler()
    else     : handler = None
    conn = eveapi.EVEAPIConnection(scheme="http", cacheHandler=handler, proxy=proxy)
    return conn.auth(keyID=user_api.keyID, vCode=user_api.vCode)


#------------------------------------------------------------------------------
class Character:
    name = ""
    characterID = 0
    corporationID = 0
    corporationName = "No Corporation"
    is_corped = False

def get_account_characters(user_api):
    connection = connect_user(user_api)
    response = connection.account.APIKeyInfo()
    corp = Corp.objects.get(id=1)
    characters = []
    if response.key.type.lower() != "account":
        raise eveapi.Error(0, "Wrong API Key type '" + response.key.type + "'. " +
                           "Please provide an API Key working for all characters of your account.")
    
    check_user_access_mask(response.key.accessMask)
    
    for char in response.key.characters:
        c = Character()
        c.name = char.characterName
        c.characterID = char.characterID
        c.corporationID = char.corporationID
        c.corporationName = char.corporationName
        c.is_corped = (char.corporationID == corp.corporationID)
        characters.append(c)
    return characters


        
#------------------------------------------------------------------------------
class CacheHandler(object):
    # Note: this is an example handler to demonstrate how to use them.
    # a -real- handler should probably be thread-safe and handle errors
    # properly (and perhaps use a better hashing scheme).

    def __init__(self, debug=False):
        self.debug = debug
        self.count = 0
        self.cache = {}
        self.tempdir = os.path.join(tempfile.gettempdir(), "eveapi")
        if not os.path.exists(self.tempdir):
            os.makedirs(self.tempdir)

    def log(self, what):
        if self.debug:
            print "[%d] %s" % (self.count, what)

    def retrieve(self, host, path, params):
        # eveapi asks if we have this request cached
        key = hash((host, path, frozenset(params.items())))

        self.count += 1  # for logging

        # see if we have the requested page cached...
        cached = self.cache.get(key, None)
        if cached:
            cacheFile = None
            #print "'%s': retrieving from memory" % path
        else:
            # it wasn't cached in memory, but it might be on disk.
            cacheFile = os.path.join(self.tempdir, str(key) + ".cache")
            if os.path.exists(cacheFile):
                self.log("%s: retrieving from disk" % path)
                f = open(cacheFile, "rb")
                cached = self.cache[key] = cPickle.loads(zlib.decompress(f.read()))
                f.close()

        if cached:
            # check if the cached doc is fresh enough
            if time.time() < cached[0]:
                self.log("%s: returning cached document" % path)
                return cached[1]  # return the cached XML doc

            # it's stale. purge it.
            self.log("%s: cache expired, purging!" % path)
            del self.cache[key]
            if cacheFile:
                os.remove(cacheFile)

        self.log("%s: not cached, fetching from server..." % path)
        # we didn't get a cache hit so return None to indicate that the data
        # should be requested from the server.
        return None

    def store(self, host, path, params, doc, obj):
        # eveapi is asking us to cache an item
        key = hash((host, path, frozenset(params.items())))


        cachedFor = obj.cachedUntil - obj.currentTime
        
        if cachedFor:
            self.log("%s: cached (%s)" % (path, str(cachedFor)))

            cachedUntil = datetime.now() + cachedFor

            # store in memory
            cached = self.cache[key] = (cachedUntil, doc)

            # store in cache folder
            cacheFile = os.path.join(self.tempdir, str(key) + ".cache")
            f = open(cacheFile, "wb")
            f.write(zlib.compress(cPickle.dumps(cached, -1)))
            f.close()
