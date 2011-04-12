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
from ecm.data.roles.models import CharacterOwnership
from ecm.data.common.models import UserAPIKey

__date__ = "2011 4 11"
__author__ = "diabeteman"

from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

#------------------------------------------------------------------------------
@login_required
def user_profile(request):
    characters = [ owned.character for owned in CharacterOwnership.objects.filter(user=request.user) ]
    api_keys = UserAPIKey.objects.filter(user=request.user)
    data = { 'characters' : characters,
            'api_keys' :  api_keys}
    return render_to_response('auth/user_profile.html', data, context_instance=RequestContext(request))