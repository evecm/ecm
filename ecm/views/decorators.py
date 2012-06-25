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

__date__ = "2011-03-08"
__author__ = "diabeteman"


import re
import binascii
import httplib as http

from django.template.context import RequestContext as Ctx
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.conf import settings

from ecm.apps.common.models import UrlPermission
from ecm.apps.hr.models import Member

#------------------------------------------------------------------------------
def basic_auth_required(username=None):
    """
    Checks for HTTP Basic authentication in the request
    """
    def decorator(view_function):
        def _wrapped_view(request, *args, **kwargs):
            host = request.get_host().split(':')[0]
            if host in ('localhost', '127.0.0.1') and not settings.BASIC_AUTH_REQUIRED_ON_LOCALHOST:
                view_function(request, *args, **kwargs)

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
def check_user_access():
    """
    Decorator for views that matches the asked URL against those configured in the database

    if the user is not logged in, redirect him/her to the login page
    if the user is allowed to consult the URL, then return to the view function
    if the page is the details of a member, check if the user owns the character.
       If so, allow the user to consult the page anyway
    if the user is not allowed, issue a "forbidden" page
    """
    def decorator(view_function):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated():
                access_ok = UrlPermission.user_has_access(request.user, request.get_full_path())
                if not access_ok:
                    try:
                        url_re = re.compile("^/members/\d+.*$")
                        if url_re.match(request.get_full_path()):
                            characterID = int(args[0])
                            access_ok = (Member.objects.get(characterID=characterID).owner == request.user)
                    except:
                        pass
                if request.user.is_superuser or access_ok:
                    return view_function(request, *args, **kwargs)
                else:
                    return forbidden(request)
            else:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
        return _wrapped_view
    return decorator

#------------------------------------------------------------------------------
def forbidden(request):
    response = render(request, 'ecm/auth/forbidden.html',
                      {'request_path' : request.get_full_path()},
                      context_instance=Ctx(request))
    response.status_code = http.FORBIDDEN
    return response

