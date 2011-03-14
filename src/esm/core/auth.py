'''
This file is part of esm

Created on 8 march 2011
@author: diabeteman
'''

import binascii
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse

import httplib as http

def basic_auth_required(username=None):
    def func_wrapper(view_function):
        def decorator(request, *args, **kwargs):
            if not request.user:
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
