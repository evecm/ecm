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

__date__ = "2011 4 17"
__author__ = "diabeteman"

from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, get_object_or_404

from ecm.view.decorators import forbidden
from ecm.core.tasks.users import update_user_accesses
from ecm.view.auth.forms import AddApiKeyForm, EditApiKeyForm
from ecm.data.roles.models import CharacterOwnership, Member
from ecm.data.common.models import UserAPIKey

#------------------------------------------------------------------------------
@login_required
def account(request):
    characters = [ owned.character for owned in CharacterOwnership.objects.filter(owner=request.user) ]
    api_keys = UserAPIKey.objects.filter(user=request.user)
    data = { 'characters' : characters,
            'api_keys' :  api_keys}
    return render_to_response('auth/account.html', data, RequestContext(request))

#------------------------------------------------------------------------------
@login_required
def add_api(request):
    if request.method == 'POST':
        form = AddApiKeyForm(request.POST)
        if form.is_valid():
            user_api = UserAPIKey()
            user_api.userID = form.cleaned_data["userID"]
            user_api.key = form.cleaned_data["apiKey"]
            user_api.user = request.user
            user_api.save()
            
            for char in form.characters:
                try:
                    owned = CharacterOwnership()
                    owned.owner = request.user
                    owned.character = Member.objects.get(characterID=char.characterID)
                    owned.save()
                except Member.DoesNotExist:
                    continue
            
            update_user_accesses(request.user)
            
            return redirect('/account')
    else: # request.method == 'GET'
        form = AddApiKeyForm()
        
    return render_to_response('auth/add_api.html', {'form': form}, RequestContext(request))

#------------------------------------------------------------------------------
@login_required
def delete_api(request, userID):
    api = get_object_or_404(UserAPIKey, userID=int(userID))
    if api.user == request.user:
        api.delete()
        return redirect("/account")
    else:
        return forbidden(request)

#------------------------------------------------------------------------------
@login_required
def edit_api(request, userID):
    api = get_object_or_404(UserAPIKey, userID=int(userID))
    if api.user != request.user:
        return forbidden(request)
    
    if request.method == 'POST':
        form = EditApiKeyForm(request.POST)
        form.user = request.user
        if form.is_valid():
            api.key = form.cleaned_data["apiKey"]
            api.is_valid = True
            api.save()
            
            for char in form.characters:
                try:
                    member = Member.objects.get(characterID=char.characterID)
                    try:
                        ownership = member.ownership
                    except CharacterOwnership.DoesNotExist:
                        ownership = CharacterOwnership()
                        ownership.character = member
                    ownership.owner = request.user
                    ownership.save()
                except Member.DoesNotExist:
                    pass
            
            update_user_accesses(request.user)
            
            return redirect('/account')
    else: # request.method == 'GET'
        form = EditApiKeyForm(initial={"userID" : api.userID, "apiKey" : api.key})
    
    data = {'form': form, 'request_path' : request.get_full_path()}
    return render_to_response('auth/edit_api.html', data, RequestContext(request))

#------------------------------------------------------------------------------
@login_required
def delete_character(request, characterID):
    character = get_object_or_404(Member, characterID=int(characterID))
    try:
        if character.ownership.owner == request.user:
            character.ownership.delete()
            update_user_accesses(request.user)
            return redirect('/account')
        else:
            return forbidden(request)
    except CharacterOwnership.DoesNotExist:
        return forbidden(request)
    
    
    
