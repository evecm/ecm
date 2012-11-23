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

__date__ = "2011 4 17"
__author__ = "diabeteman"

from django.template.context import RequestContext as Ctx
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db import transaction

from ecm.views.decorators import forbidden
from ecm.apps.hr.tasks.users import update_user_accesses
from ecm.views.account import init_characters
from ecm.views.account.forms import AddApiKeyForm, EditApiKeyForm, AddBindingForm
from ecm.apps.hr.models import Member
from ecm.apps.common.models import UserAPIKey, ExternalApplication, UserBinding, Motd
from ecm.apps.common.api import required_access_mask

import logging
logger = logging.getLogger(__name__)

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
    try:
        motd = Motd.objects.latest()
    except Motd.DoesNotExist:
        motd = None
    data = {
        'characters'    : Member.objects.filter(owner=request.user),
        'api_keys'      : UserAPIKey.objects.filter(user=request.user),
        'external_apps' : external_apps,
        'motd'          : motd
    }
    return render_to_response('ecm/auth/account.html', data, Ctx(request))

#------------------------------------------------------------------------------
@login_required
@transaction.commit_on_success
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

            members, corps = init_characters(request.user, form.characters)
            
            for corp in corps:
                corp.save()
            for member in members:
                member.save()
            
            update_user_accesses(request.user)
            
            logger.info('"%s" added new API Key %d' % (request.user, user_api.keyID))

            return redirect('/account/')
    else: # request.method == 'GET'
        form = AddApiKeyForm()

    data = {
        'form': form,
        'accessMask': required_access_mask(character=True)
    }

    return render_to_response('ecm/auth/add_api.html', data, Ctx(request))

#------------------------------------------------------------------------------
@login_required
@transaction.commit_on_success
def delete_api(request, keyID):
    api = get_object_or_404(UserAPIKey, keyID=int(keyID))
    if api.user == request.user:
        keyID = api.keyID
        api.delete()
        logger.info('"%s" deleted API Key %d' % (request.user, keyID))
        return redirect("/account/")
    else:
        return forbidden(request)

#------------------------------------------------------------------------------
@login_required
@transaction.commit_on_success
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

            members, corps = init_characters(request.user, form.characters)
            
            for member in members:
                member.save()
            for corp in corps:
                corp.save()
            
            update_user_accesses(request.user)
            
            logger.info('"%s" edited API Key %d' % (request.user, api.keyID))

            return redirect('/account/')
    else: # request.method == 'GET'
        form = EditApiKeyForm(initial={"keyID" : api.keyID, "vCode" : api.vCode})

    data = {
        'form': form,
        'request_path' : request.get_full_path(),
        'accessMask': required_access_mask(character=True)
    }
    return render_to_response('ecm/auth/edit_api.html', data, Ctx(request))

#------------------------------------------------------------------------------
@login_required
@transaction.commit_on_success
def delete_character(request, characterID):
    character = get_object_or_404(Member, characterID=int(characterID))
    if character.owner == request.user:
        character.owner = None
        character.save()
        update_user_accesses(request.user)
        logger.info('"%s" gave up ownership of character "%s"' % (request.user, character.name))
        return redirect('/account/')
    else:
        return forbidden(request)

#------------------------------------------------------------------------------
@login_required
@transaction.commit_on_success
def add_binding(request, app_id):
    app = get_object_or_404(ExternalApplication, id=int(app_id))
    if request.method == 'POST':
        form = AddBindingForm(request.POST, app=app, user=request.user)
        if form.is_valid():
            UserBinding.objects.create(user=request.user,
                                       external_app=app,
                                       external_id=form.external_id,
                                       external_name=form.cleaned_data['username'])
            logger.info('"%s" enabled binding to external application "%s" with external_id=%d'
                        % (request.user, app.name, form.external_id))
            return redirect('/account/')
    else: # request.method == 'GET'
        form = AddBindingForm(app=app)

    data = {'form': form, 'request_path' : request.get_full_path(), 'app': app}
    return render_to_response('ecm/auth/add_binding.html', data, Ctx(request))

#------------------------------------------------------------------------------
@login_required
@transaction.commit_on_success
def delete_binding(request, binding_id):
    binding = get_object_or_404(UserBinding, id=int(binding_id))
    if binding.user == request.user:
        binding.delete()
        logger.info('"%s" removed binding to external application "%s"'
                        % (request.user, binding.external_app.name))
        return redirect('/account/')
    else:
        return forbidden(request)
