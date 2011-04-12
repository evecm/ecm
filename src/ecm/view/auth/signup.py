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

__date__ = "2011 4 5"
__author__ = "diabeteman"


from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.db import transaction
from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from ecm.data.common.models import UserAPIKey, RegistrationProfile
from ecm.data.roles.models import CharacterOwnership
from ecm.data.common.forms import AccountCreationForm

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
            user_api.userID = form.cleaned_data["userID"]
            user_api.key = form.cleaned_data["apiKey"]
            user_api.user = user
            user_api.save()
            
            for char in form.characters:
                if char.is_corped:
                    owned = CharacterOwnership()
                    owned.user = user
                    owned.character_id = char.characterID
                    owned.save()
            
            send_activation_email(request, profile)
            
            return render_to_response('auth/account_created.html', 
                                      { 'form': form }, 
                                      context_instance=RequestContext(request))
    else: # request.method == 'GET'
        form = AccountCreationForm()
        
    return render_to_response('auth/create_account.html', 
                              { 'form': form }, 
                              context_instance=RequestContext(request))

#------------------------------------------------------------------------------
def activate_account(request, activation_key):
    try:
        user = RegistrationProfile.objects.activate_user(activation_key)
        return render_to_response('auth/account_activated.html', 
                                  { 'activated_user' : user }, 
                                  context_instance=RequestContext(request))
    except (ValueError, UserWarning) as err:
        return render_to_response('auth/activation_error.html', 
                                  { 'activation_key': activation_key,
                                   'error_reason': str(err) }, 
                                  context_instance=RequestContext(request))
    



def send_activation_email(request, user_profile):
    ctx_dict = {'site': settings.ECM_BASE_URL,
                'user_name': user_profile.user.username,
                'activation_key': user_profile.activation_key,
                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS}
    subject = render_to_string('auth/activation_email_subject.txt',
                               ctx_dict, context_instance=RequestContext(request))
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    
    txt_content = render_to_string('auth/activation_email.txt',
                                   ctx_dict, context_instance=RequestContext(request))
    html_content = render_to_string('auth/activation_email.html',
                                    ctx_dict, context_instance=RequestContext(request))
    msg = EmailMultiAlternatives(subject, 
                                 body=txt_content,
                                 to=[user_profile.user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
