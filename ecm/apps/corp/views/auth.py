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

import logging
import httplib as http

from django.http import HttpResponse, HttpResponseBadRequest

from ecm.apps.corp.models import Corporation
from ecm.utils import crypto

LOG = logging.getLogger(__name__)

AUTH_SECRET = '_auth_secret'
AUTH_FINGERPRINT = '_auth_fingerprint'
SESSION_AUTHENTICATED = '_session_authenticated'

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
    
    if AUTH_FINGERPRINT in request.session:
        if request.session[AUTH_FINGERPRINT] != key_fingerprint:
            # to avoid taking over another TrustedCorp's session, we flush all the data.
            request.session.flush()
    else:
        request.session.cycle_key()
    request.session.set_expiry(600) # set expiry to 10 minutes
    
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
def active_session_required():
    """
    Checks for a previously authenticated session
    """
    def decorator(view_function):
        
        def _wrapped_view(request, *args, **kwargs):
            
            key_fingerprint = request.session.get(AUTH_FINGERPRINT)
            session_authenticated = request.session.get(SESSION_AUTHENTICATED)
            
            if key_fingerprint and session_authenticated:
                try:
                    request.corp = Corporation.objects.get(key_fingerprint=key_fingerprint)
                except Corporation.DoesNotExist:
                    return HttpResponse(status=http.UNAUTHORIZED)
                
                return view_function(request, *args, **kwargs)
            else:
                return HttpResponse(status=http.UNAUTHORIZED)

        return _wrapped_view

    return decorator


