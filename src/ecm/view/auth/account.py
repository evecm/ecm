# Copyright (c) 2010-2011 Robin Jarry
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

__date__ = "2011 4 17"
__author__ = "diabeteman"

from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, get_object_or_404

from ecm.view.decorators import forbidden
from ecm.core.tasks.users import update_user_accesses
from ecm.view.auth.forms import AddApiKeyForm, EditApiKeyForm
from ecm.data.roles.models import Member
from ecm.data.common.models import UserAPIKey

#------------------------------------------------------------------------------
@login_required
def account(request):
    characters = Member.objects.filter(owner=request.user)
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
                if char.is_corped:
                    try:
                        character = Member.objects.get(characterID=char.characterID)
                        character.owner = request.user
                        character.save()
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
                if char.is_corped:
                    try:
                        member = Member.objects.get(characterID=char.characterID)
                        member.owner = request.user
                        member.save()
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
    if character.owner == request.user:
        character.owner = None
        character.save()
        update_user_accesses(request.user)
        return redirect('/account')
    else:
        return forbidden(request)
    
    
    
