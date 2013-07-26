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

__date__ = '2012 08 01'
__author__ = 'diabeteman'

import zlib
import logging
import httplib as http
from functools import wraps

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest

from ecm.apps.corp.models import Corporation
from ecm.utils import crypto
from ecm.utils import _json as json

LOG = logging.getLogger(__name__)

AUTH_SECRET = '_auth_secret'
AUTH_FINGERPRINT = '_auth_fingerprint'
SESSION_AUTHENTICATED = '_session_authenticated'
# Max 5 minutes before session is invalidated. 
# session time will be extended by 5 minutes each time the client makes a new request.
SESSION_LENGTH = 300 

#------------------------------------------------------------------------------
def get_challenge(request):
    """
    This function will check for the Http-Authorization: header in the request.
    
    If found, it will look in the db for a TrustedCorp that has the given public key
    fingerprint. 
    
    Then, it will encode a randomly generated secret with the TrustedCorp's public key.
    
    Store the secret in the current session and send the encrypted secret back to the client. 
    """
    
    auth_string = request.META.get('HTTP_AUTHORIZATION', None)
    
    if auth_string is None:
        return HttpResponse('Missing Authorization header', status=http.UNAUTHORIZED)
    
    (auth_method, key_fingerprint) = auth_string.split(' ', 1)
    
    # RSA is not an official http auth method but who cares :D 
    if not auth_method.upper() == 'RSA':
        return HttpResponseBadRequest("Bad auth method: %r. Please use 'RSA'." % auth_method)

    key_fingerprint = key_fingerprint.strip()
    
    try:
        corp = Corporation.objects.get(key_fingerprint=key_fingerprint)
    except Corporation.DoesNotExist:
        return HttpResponse("Key fingerprint not found, we don't know you.", status=http.UNAUTHORIZED)
    
    if not corp.is_trusted:
        return HttpResponse('Your corporation is not trusted by our server.', status=http.UNAUTHORIZED)
    
    if AUTH_FINGERPRINT in request.session:
        if request.session[AUTH_FINGERPRINT] != key_fingerprint:
            # to avoid taking over another TrustedCorp's session, we flush all the data.
            request.session.flush()
    else:
        request.session.cycle_key()
    request.session.set_expiry(SESSION_LENGTH)
    
    # we store the key_fingerprint to tie this session to the TrustedCorp 
    request.session[AUTH_FINGERPRINT] = key_fingerprint
    request.session[AUTH_SECRET] = crypto.generate_secret()
    
    encrypted_secret = crypto.rsa_encrypt(corp.public_key, request.session[AUTH_SECRET])
    
    return HttpResponse(encrypted_secret)  


#------------------------------------------------------------------------------
def post_response(request):
    
    key_fingerprint = request.session.get(AUTH_FINGERPRINT)
    secret = request.session.get(AUTH_SECRET)
    
    if key_fingerprint is None or secret is None:
        return HttpResponse(status=http.UNAUTHORIZED)
    
    given_secret = crypto.rsa_decrypt(Corporation.objects.mine().private_key, request.body)
    
    if given_secret == secret:
        # authentication successful!
        request.session[SESSION_AUTHENTICATED] = True
        return HttpResponse(status=http.ACCEPTED)
    else:
        return HttpResponse(status=http.UNAUTHORIZED)

#------------------------------------------------------------------------------
def valid_session_required(view_function):
    """
    Decorator that checks for a previously authenticated session
    
    If the session is valid, it checks that the corp which is making the request
    has access to the requested URL
    """
    @wraps(view_function)
    def _wrapped_view(request, *args, **kwargs):
        
        key_fingerprint = request.session.get(AUTH_FINGERPRINT)
        session_authenticated = request.session.get(SESSION_AUTHENTICATED)
        
        if key_fingerprint and session_authenticated:
            try:
                path = request.get_full_path()
                corp = Corporation.objects.get(key_fingerprint=key_fingerprint)
                if corp.is_trusted and (path == '/corp/share/allowed/'
                                        or corp.get_allowed_shares().filter(url=path)):
                    request.corp = corp
                else:
                    return HttpResponse(status=http.UNAUTHORIZED)
            except Corporation.DoesNotExist:
                return HttpResponse(status=http.UNAUTHORIZED)
            
            # extend session time at each new request
            request.session.set_expiry(SESSION_LENGTH)
            
            return view_function(request, *args, **kwargs)
        else:
            return HttpResponse(status=http.UNAUTHORIZED)

    return _wrapped_view


#------------------------------------------------------------------------------
@csrf_exempt
def start_session(request):
    if request.method == 'POST':
        return post_response(request)
    else:
        return get_challenge(request)

#------------------------------------------------------------------------------
def end_session(request):
    if request.session.get(SESSION_AUTHENTICATED):
        # we reset the session
        request.session.flush()
        # then return something to tell it's ok
        return HttpResponse()
    else:
        return HttpResponseBadRequest('No valid session found')

#------------------------------------------------------------------------------
def encrypted_response(request, data, compress=False):
    if not isinstance(data, basestring):
        data = json.dumps(data)
    if compress:
        data = zlib.compress(data)
        mime = 'application/gzip-compressed'
    else:
        mime = 'application/octet-stream'
    encrypted_data = crypto.aes_encrypt(request.session[AUTH_SECRET], data)
    return HttpResponse(encrypted_data, mimetype=mime)

