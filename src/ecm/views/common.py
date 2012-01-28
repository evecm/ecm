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
from ecm.apps.common.models import Setting

__date__ = "2010-05-16"
__author__ = "diabeteman"


import re

from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.context import RequestContext as Ctx
from django.db import transaction
from django import forms
from django.utils.translation import ugettext_lazy as _

from ecm.core.eve.validators import validate_director_api_key
from ecm.core.eve import api
from ecm.apps.hr.models import Member
from ecm.apps.corp.models import Corp

#------------------------------------------------------------------------------
SHOWINFO_PATTERN = re.compile(r"showinfo:13\d\d//(\d+)", re.IGNORECASE + re.DOTALL)
@login_required
def corp(request):

    try:
        api.get_api()
    except Setting.DoesNotExist:
        # this should fail only on first install and redirect to the
        # edit api key form.
        return redirect('/editapi/')

    try:
        corp = Corp.objects.get(id=1)
        corp.description = SHOWINFO_PATTERN.subn(r"/hr/members/\1/", corp.description)[0]
        corp.memberCount = Member.objects.filter(corped=True).count()
    except Corp.DoesNotExist:
        corp = Corp(corporationName="No Corporation info")

    data = { 'corp' : corp }

    return render_to_response("common/corp.html", data, Ctx(request))


#------------------------------------------------------------------------------
@user_passes_test(lambda u: u.is_superuser)
@transaction.commit_on_success
def edit_apikey(request):
    if request.method == 'POST':
        form = DirectorApiKeyForm(request.POST)
        if form.is_valid():
            keyID = form.cleaned_data.get('keyID')
            vCode = form.cleaned_data.get('vCode')
            characterID = form.cleaned_data.get('characterID')
            api.set_api(keyID, vCode, characterID)
            return redirect('/')
    else:
        try:
            keyID = Setting.objects.get(name='common_api_keyID').getValue()
            vCode = Setting.objects.get(name='common_api_vCode').getValue()
            characterID = Setting.objects.get(name='common_api_characterID').getValue()
        except Setting.DoesNotExist:
            keyID = 0
            vCode = ''
            characterID = 0
        form = DirectorApiKeyForm(initial={
            'keyID': keyID,
            'vCode': vCode,
            'characterID': characterID
        })
    return render_to_response('common/edit_director_api.html',
                              {'form': form}, Ctx(request))




#------------------------------------------------------------------------------
class DirectorApiKeyForm(forms.Form):
    keyID = forms.IntegerField(label=_("API Key ID"))
    characterID = forms.IntegerField(label=_('Character ID'))
    vCode = forms.CharField(label=_("Verification Code"),
                            widget=forms.TextInput(attrs={'size':'100'}))

    def clean(self):
        cleaned_data = self.cleaned_data

        keyID = cleaned_data.get("keyID")
        vCode = cleaned_data.get("vCode")
        characterID = cleaned_data.get("characterID")

        validate_director_api_key(keyID, vCode, characterID)

        return cleaned_data

