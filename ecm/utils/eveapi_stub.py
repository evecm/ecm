# Copyright (c) 2010-2013 Robin Jarry
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

__date__ = "2013-03-08"
__author__ = "diabeteman"

import os

from django.conf import settings

from ecm.lib.eveapi import Error, RequestError, AuthenticationError, ServerError #@UnusedImport 
from ecm.lib.eveapi import _ParseXML, _RootContext


#-----------------------------------------------------------------------------
def EVEAPIConnection(url="api.eveonline.com", cacheHandler=None, proxy=None, proxySSL=False):
    return _RootContextStub(None, '', {}, {})


#-----------------------------------------------------------------------------
class _RootContextStub(_RootContext):

    def __call__(self, path, **kw):
        
        stub_root = settings.EVEAPI_STUB_FILES_ROOT
        
        if not stub_root:
            import ecm
            stub_root = os.path.join(os.path.dirname(ecm.__file__), 'tests/eveapi_responses')
        
        if not os.path.isdir(stub_root):
            stub_root = None
        
        if stub_root:
            # convert absolute path to relative path
            path = path.strip('/') + '.xml'
            response_file = os.path.join(stub_root, path)
            return _ParseXML(open(response_file, 'r'), True, False)
        else:
            raise UserWarning('Variable "EVEAPI_STUB_FILES_ROOT" is not set in settings.py or set to an invalid directory.')
