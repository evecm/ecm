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
import httplib as http
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.

from django.template.context import RequestContext
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser, Group
from django.utils.decorators import available_attrs
from django.http import HttpResponse
from django.conf import settings

from ecm.data.roles.models import CharacterOwnership

#------------------------------------------------------------------------------
def basic_auth_required(username=None):
    def decorator(view_function):
        @wraps(view_function, assigned=available_attrs(view_function))
        def _wrapped_view(request, *args, **kwargs):
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
                if username and not (request.user.username == username
                                  or request.user.is_superuser):
                    return HttpResponse(status=http.FORBIDDEN)
                else:
                    return view_function(request, *args, **kwargs)
            else:
                return HttpResponse(status=http.UNAUTHORIZED)
            
        return _wrapped_view
    
    return decorator


#------------------------------------------------------------------------------
def user_member_of(group_ids):
    """
    Decorator for views that checks that the user is in at least in one of the
    groups given as parameters, redirecting to the log-in page if necessary.
    
    If the user is authenticated and is not member of any group, the decorator 
    redirects the user to an "unauthorized" page.
    """
    def decorator(view_function):
        @wraps(view_function, assigned=available_attrs(view_function))
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated():
                if request.user.is_superuser or request.user.groups.filter(id__in=group_ids):
                    return view_function(request, *args, **kwargs)
                else:
                    return forbidden(request)
            else:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
        return _wrapped_view
    return decorator

#------------------------------------------------------------------------------
def user_is_director():
    """
    Decorator that checks if the user has at least one corped character 
    who has the in-game 'director' role
    """
    return user_member_of([settings.DIRECTOR_GROUP_ID])

#------------------------------------------------------------------------------
def user_owns_character():
    def decorator(view_function):
        @wraps(view_function, assigned=available_attrs(view_function))
        def _wrapped_view(request, characterID, *args, **kwargs):
            if request.user.is_authenticated():
                try:
                    user = CharacterOwnership.objects.get(character=characterID).owner
                except CharacterOwnership.DoesNotExist:
                    user = AnonymousUser()
                
                if user == request.user or request.user.is_superuser or request.user.groups.filter(id=settings.DIRECTOR_GROUP_ID):
                    return view_function(request, characterID, *args, **kwargs)
                else:
                    return forbidden(request)
            else:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
        return _wrapped_view
    return decorator

#------------------------------------------------------------------------------
def user_has_titles():
    """
    Decorator that checks if the user has at least one corped character 
    who has at least one Title assigned.
    """
    return user_member_of(settings.ALL_GROUP_IDS)

#------------------------------------------------------------------------------
def forbidden(request):
    response = render(request, 'auth/forbidden.html',
                      {'request_path' : request.get_full_path()},
                      context_instance=RequestContext(request))
    response.status_code = http.FORBIDDEN
    return response

#------------------------------------------------------------------------------
try:
    g = Group.objects.get(id=settings.DIRECTOR_GROUP_ID)
    if g.name != settings.DIRECTOR_GROUP_NAME:
        g.name = settings.DIRECTOR_GROUP_NAME
        g.save()
except Group.DoesNotExist:
    Group.objects.create(id=settings.DIRECTOR_GROUP_ID, 
                         name=settings.DIRECTOR_GROUP_NAME)
