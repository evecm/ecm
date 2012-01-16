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

__date__ = "2011 4 5"
__author__ = "diabeteman"


from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.db import transaction
from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives

from ecm.apps.hr.tasks.users import update_user_accesses
from ecm.apps.common.models import UserAPIKey, RegistrationProfile
from ecm.apps.hr.models import Member
from ecm.views.auth.forms import AccountCreationForm
from ecm.core.eve.validators import user_access_mask

import logging
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def create_account(request):
    if request.method == 'POST':
        form = AccountCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            email = form.cleaned_data["email"]
            user, profile = RegistrationProfile.objects.create_inactive_user(username=username,
                                                                             email=email,
                                                                             password=password)
            user_api = UserAPIKey()
            user_api.keyID = form.cleaned_data["keyID"]
            user_api.vCode = form.cleaned_data["vCode"]
            user_api.user = user
            user_api.save()

            for char in form.characters:
                if char.is_corped:
                    try:
                        character = Member.objects.get(characterID=char.characterID)
                        character.owner = user
                        character.save()
                    except Member.DoesNotExist:
                        continue

            logger.info('"%s" created new account id=%d' % (user, user.id))
            send_activation_email(request, profile)
            logger.info('activation email sent to "%s" for account "%s"' % (user.email, user))

            return render_to_response('auth/account_created.html',
                                      { 'form': form },
                                      context_instance=RequestContext(request))
    else: # request.method == 'GET'
        form = AccountCreationForm()

    accessMask = user_access_mask()

    return render_to_response('auth/create_account.html',
                              { 'form': form, 'accessMask': accessMask },
                              context_instance=RequestContext(request))

#------------------------------------------------------------------------------
def activate_account(request, activation_key):
    try:
        user = RegistrationProfile.objects.activate_user(activation_key)
        update_user_accesses(user)
        logger.info('account "%s" activated' % (user.username))
        return render_to_response('auth/account_activated.html',
                                  { 'activated_user' : user },
                                  context_instance=RequestContext(request))
    except (ValueError, UserWarning), err:
        logger.info('could not use activation key "%s": %s' % (activation_key, str(err)))
        return render_to_response('auth/activation_error.html',
                                  { 'activation_key': activation_key,
                                   'error_reason': str(err) },
                                  context_instance=RequestContext(request))



#------------------------------------------------------------------------------
def send_activation_email(request, user_profile):
    ctx_dict = {'site': settings.ECM_BASE_URL,
                'user_name': user_profile.user.username,
                'activation_key': user_profile.activation_key,
                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS}
    subject = render_to_string('auth/activation_email_subject.txt',
                               ctx_dict, context_instance=RequestContext(request))
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())

    txt_content = render_to_string('auth/activation_email.txt', ctx_dict, RequestContext(request))
    html_content = render_to_string('auth/activation_email.html', ctx_dict, RequestContext(request))
    msg = EmailMultiAlternatives(subject,
                                 body=txt_content,
                                 to=[user_profile.user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
