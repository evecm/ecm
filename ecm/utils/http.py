# Copyright (c) 2010-2012 Robin Jarry
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

__date__ = '2012-08-07'
__author__ = 'diabeteman'

import urllib
import urllib2
import cookielib


class HttpClient(object):
    
    def __init__(self):
        self.cookie_jar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
        
    def get(self, url, params=None, headers=None):
        if params is not None:
            url += '?' + urllib.urlencode(params)
        
        request = urllib2.Request(url)
        
        if headers is not None:
            for key, val in headers.items():
                request.add_header(key, val)
        
        return self.opener.open(request)
    
    def post(self, url, body, headers=None):
        request = urllib2.Request(url)
        try:
            request.add_header('X-CSRFToken', self.get_cookie('csrftoken'))
        except KeyError:
            pass
        
        if headers is not None:
            for key, val in headers.items():
                request.add_header(key, val)
        
        return self.opener.open(url, body)
    
    def get_cookie(self, name):
        for cookie in self.cookie_jar:
            if cookie.name == name:
                return cookie.value
        raise KeyError(name)
