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

from __future__ import with_statement

__date__ = '2010-05-16'
__author__ = 'diabeteman'

import re

from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.context import RequestContext as Ctx
from django.db import transaction
from django import forms
from django.utils.translation import ugettext_lazy as _

from ecm.apps.scheduler.models import ScheduledTask
from ecm.apps.scheduler.main import Scheduler
from ecm.apps.common.models import Setting
from ecm.apps.eve.validators import validate_director_api_key
from ecm.apps.eve import api
from ecm.apps.hr.models import Member
from ecm.apps.corp.models import Corp

#------------------------------------------------------------------------------
SHOWINFO_PATTERN = re.compile(r'showinfo:13\d\d//(\d+)')
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
        corp.description = SHOWINFO_PATTERN.sub(r'/hr/members/\1/', corp.description)
        corp.memberCount = Member.objects.filter(corped=True).count()
    except Corp.DoesNotExist:
        corp = Corp(corporationName='No Corporation info')

    data = { 'corp' : corp }

    return render_to_response('common/corp.html', data, Ctx(request))


#------------------------------------------------------------------------------
@user_passes_test(lambda u: u.is_superuser)
def edit_apikey(request):
    if request.method == 'POST':
        form = DirectorApiKeyForm(request.POST)
        if form.is_valid():
            keyID = form.cleaned_data.get('keyID')
            vCode = form.cleaned_data.get('vCode')
            characterID = form.cleaned_data.get('characterID')
            
            with transaction.commit_manually():
                try:
                    api.set_api(keyID, vCode, characterID)
                    tasks_to_execute = ScheduledTask.objects.filter(is_active=True).order_by("-priority")
                    tasks_to_execute.update(is_scheduled=True)
                except:
                    transaction.rollback()
                    raise
                else:
                    transaction.commit()
                
            Scheduler.instance().schedule(*list(tasks_to_execute))
            
            return redirect('/scheduler/tasks/')
    else:
        try:
            keyID = Setting.get('common_api_keyID')
            vCode = Setting.get('common_api_vCode')
        except Setting.DoesNotExist:
            keyID = 0
            vCode = ''
        form = DirectorApiKeyForm(initial={
            'keyID': keyID,
            'vCode': vCode,
        })
    return render_to_response('common/edit_director_api.html',
                              {'form': form}, Ctx(request))




#------------------------------------------------------------------------------
class DirectorApiKeyForm(forms.Form):
    keyID = forms.IntegerField(label=_('API Key ID'))
    vCode = forms.CharField(label=_('Verification Code'),
                            widget=forms.TextInput(attrs={'size':'100'}))

    def clean(self):
        cleaned_data = self.cleaned_data

        keyID = cleaned_data.get('keyID')
        vCode = cleaned_data.get('vCode')

        characterID = validate_director_api_key(keyID, vCode)
        
        cleaned_data['characterID'] = characterID

        return cleaned_data

