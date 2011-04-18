# The MIT License - EVE Corporation Management
# 
# Copyright (c) 2010 Robin Jarry
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__date__ = "2010-03-23"
__author__ = "diabeteman"

import cPickle, os, tempfile, time, zlib
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from ecm.lib import eveapi

from ecm.data.common.models import APIKey
from ecm.data.corp.models import Corp

#------------------------------------------------------------------------------
def get_api():
    try:
        return APIKey.objects.all().order_by("-id")[0]
    except IndexError:
        raise ObjectDoesNotExist("There is no APIKey registered in the database")

#------------------------------------------------------------------------------
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

#------------------------------------------------------------------------------
def connect(proxy=None, cache=False):
    """
    Creates a connection to the web API with director credentials 
    """
    if cache : handler = CacheHandler()
    else     : handler = None
    conn = eveapi.EVEAPIConnection(scheme="https", cacheHandler=handler, proxy=proxy)
    api = get_api()
    return conn.auth(userID=api.userID, apiKey=api.key)

#------------------------------------------------------------------------------
def connect_user(user_api, proxy=None, cache=False):
    """
    Creates a connection to the web API with a user's credentials
    """
    if cache : handler = CacheHandler()
    else     : handler = None
    conn = eveapi.EVEAPIConnection(scheme="http", cacheHandler=handler, proxy=proxy)
    return conn.auth(userID=user_api.userID, apiKey=user_api.key)



#------------------------------------------------------------------------------
class Character:
    name = ""
    characterID = 0
    corporationID = 0
    corporationName = "No Corporation"
    is_corped = False

def get_account_characters(user_api):
    connection = connect_user(user_api)
    response = connection.account.Characters()
    corp = Corp.objects.get(id=1)
    characters = []
    for char in response.characters:
        c = Character()
        c.name = char.name
        c.characterID = char.characterID
        c.corporationID = char.corporationID
        c.corporationName = char.corporationName
        c.is_corped = char.corporationID == corp.corporationID
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
