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

__date__ = "2011-03-08"
__author__ = "diabeteman"


import binascii
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse

import httplib as http

def basic_auth_required(username=None):
    def func_wrapper(view_function):
        def decorator(request, *args, **kwargs):
            if request.user in (False, None, AnonymousUser()):
                auth_string = request.META.get('HTTP_AUTHORIZATION', None)
            
                if not auth_string:
                    return HttpResponse(status=http.UNAUTHORIZED)
                    
                try:
                    (auth_method, auth_credentials) = auth_string.split(" ", 1)
            
                    if not auth_method.lower() == 'basic':
                        return HttpResponse(status=http.UNAUTHORIZED)
            
                    auth_credentials = auth_credentials.strip().decode('base64')
                    user, pwd = auth_credentials.split(':', 1)
                except (ValueError, binascii.Error):
                    return HttpResponse(status=http.UNAUTHORIZED)
            
                request.user = authenticate(username=user, password=pwd) or AnonymousUser()
            
            if not request.user in (False, None, AnonymousUser()):
                if username and not request.user.username == username:
                    if not (request.user.is_superuser or request.user.is_staff):
                        return HttpResponse(status=http.FORBIDDEN)
                return view_function(request, *args, **kwargs)
            else:
                return HttpResponse(status=http.UNAUTHORIZED)
            
        return decorator
    
    return func_wrapper
