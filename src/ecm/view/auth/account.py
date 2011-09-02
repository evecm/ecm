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
from ecm.view.auth.forms import AddApiKeyForm, EditApiKeyForm, AddBindingForm
from ecm.data.roles.models import Member
from ecm.data.common.models import UserAPIKey, ExternalApplication, UserBinding

#------------------------------------------------------------------------------
@login_required
def account(request):
    external_apps = []
    for app in ExternalApplication.objects.select_related(depth=2).all():
        try:
            binding = app.user_bindings.all().get(user=request.user)
        except UserBinding.DoesNotExist:
            binding = None 
        external_apps.append({'app': app, 'binding': binding})
    
    data = { 
        'characters' : Member.objects.filter(owner=request.user),
        'api_keys' :  UserAPIKey.objects.filter(user=request.user),
        'external_apps' : external_apps
    }
    return render_to_response('auth/account.html', data, RequestContext(request))

#------------------------------------------------------------------------------
@login_required
def add_api(request):
    if request.method == 'POST':
        form = AddApiKeyForm(request.POST)
        form.user = request.user
        if form.is_valid():
            user_api = UserAPIKey()
            user_api.keyID = form.cleaned_data["keyID"]
            user_api.vCode = form.cleaned_data["vCode"]
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
def delete_api(request, keyID):
    api = get_object_or_404(UserAPIKey, keyID=int(keyID))
    if api.user == request.user:
        api.delete()
        return redirect("/account")
    else:
        return forbidden(request)

#------------------------------------------------------------------------------
@login_required
def edit_api(request, keyID):
    api = get_object_or_404(UserAPIKey, keyID=int(keyID))
    if api.user != request.user:
        return forbidden(request)
    
    if request.method == 'POST':
        form = EditApiKeyForm(request.POST)
        form.user = request.user
        if form.is_valid():
            api.vCode = form.cleaned_data["vCode"]
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
        form = EditApiKeyForm(initial={"keyID" : api.keyID, "vCode" : api.vCode})
    
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
    
#------------------------------------------------------------------------------
@login_required
def add_binding(request, app_id):
    app = get_object_or_404(ExternalApplication, id=int(app_id))
    if request.method == 'POST':
        form = AddBindingForm(request.POST, app=app, user=request.user)
        if form.is_valid():
            UserBinding.objects.create(user=request.user, 
                                       external_app=app, 
                                       external_id=form.external_id, 
                                       external_name=form.cleaned_data['username'])
            return redirect('/account')
    else: # request.method == 'GET'
        form = AddBindingForm(app=app)
    
    data = {'form': form, 'request_path' : request.get_full_path(), 'app': app}
    return render_to_response('auth/add_binding.html', data, RequestContext(request))

#------------------------------------------------------------------------------
@login_required
def delete_binding(request, binding_id):
    binding = get_object_or_404(UserBinding, id=int(binding_id))
    if binding.user == request.user:
        binding.delete()
        return redirect('/account')
    else:
        return forbidden(request)
