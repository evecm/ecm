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
from django.conf import settings

__date__ = "2011 4 6"
__author__ = "diabeteman"

from django import forms
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.template import loader
from django.utils.http import int_to_base36
from django.template import Context
from django.utils.translation import ugettext_lazy as _

from captcha.fields import CaptchaField

from ecm.core import api
from ecm.data.common.models import UserAPIKey
from ecm.lib import eveapi
from ecm.data.roles.models import CharacterOwnership, Member
from ecm.view.auth.fields import PasswordField

#------------------------------------------------------------------------------
class AccountCreationForm(forms.Form):

    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^[\w.@+-]+$',
                                help_text=_("Required. Less 30 characters. "
                                          "Letters, digits and @/./+/-/_ only."),
                                error_messages = {'invalid': _("This field may contain only letters, "
                                                  "numbers and @/./+/-/_ characters.")})
    email = forms.EmailField(label=_("E-Mail address"))
    password1 = PasswordField(label=_("Password"), min_length=6)
    password2 = PasswordField(label=_("Password (confirmation)"), min_length=6,
                                help_text=_("Enter the same password as above, for verification."))
    userID = forms.IntegerField(label="User ID")
    apiKey = forms.CharField(label=_("Limited API Key"), min_length=64, max_length=64)
    captcha = CaptchaField()
    characters = []
    
    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already in use.
        """
        try:
            User.objects.get(username__iexact=self.cleaned_data['username'])
            raise forms.ValidationError(_("A user with that username already exists."))
        except User.DoesNotExist:
            return self.cleaned_data['username']
    
    def clean_email(self):
        """
        Validate that the supplied email address is unique for the site.
        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("This email address is already in use."))
        return self.cleaned_data['email']
    
    def clean_userID(self):
        """
        Validate that the supplied userID is not already associated to another User.
        """
        if UserAPIKey.objects.filter(userID=self.cleaned_data['userID']):
            raise forms.ValidationError(_("This EVE account is already registered."))
        return self.cleaned_data['userID']
    
    def clean(self):
        cleaned_data = self.cleaned_data
        
        userID = cleaned_data.get("userID")
        apiKey = cleaned_data.get("apiKey")
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        
        if not None in (userID, apiKey, username, email, password1, password2):
            # test if both password fields match
            if not password1 == password2:
                self._errors["password2"] = self.error_class([_("Passwords don't match")])
                del cleaned_data["password2"]
            
            # test if API credentials are valid and if EVE account contains 
            # characters which are members of the corporation
            try:
                self.characters = api.get_account_characters(UserAPIKey(userID=userID, key=apiKey))
                valid_account = False
                for c in self.characters:
                    exists = Member.objects.filter(characterID=c.characterID).exists()
                    valid_account |= exists and c.is_corped
                if valid_account:
                    ids = [ c.characterID for c in self.characters ]
                    if CharacterOwnership.objects.filter(character__in=ids):
                        self._errors["userID"] = self.error_class([_("A character from this account is already registered by another player")])
                        del cleaned_data["userID"]
                else:
                    self._errors["userID"] = self.error_class([_("This EVE account has no character member of the corporation")])
                    del cleaned_data["userID"]
            except eveapi.Error as e:
                self._errors["userID"] = self.error_class([str(e)])
                self._errors["apiKey"] = self.error_class([str(e)])
                del cleaned_data["userID"]
                del cleaned_data["apiKey"]

        return cleaned_data

#------------------------------------------------------------------------------
class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("E-mail"), max_length=75)
    captcha = CaptchaField()

    def clean_email(self):
        """
        Validates that an active user exists with the given e-mail address.
        """
        email = self.cleaned_data["email"]
        self.users_cache = User.objects.filter(
                                email__iexact=email,
                                is_active=True
                            )
        if len(self.users_cache) == 0:
            raise forms.ValidationError(_("That e-mail address doesn't have an associated user account. Are you sure you've registered?"))
        return email

    def save(self, domain_override=settings.ECM_BASE_URL, email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator, from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the user
        """
        from django.core.mail import send_mail
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            t = loader.get_template(email_template_name)
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            send_mail(_("Password reset on %s") % site_name,
                t.render(Context(c)), from_email, [user.email])

#------------------------------------------------------------------------------
class PasswordSetForm(forms.Form):
    """
    A form that lets a user change set his/her password without
    entering the old password
    """
    new_password1 = PasswordField(label=_("New password"), min_length=6)
    new_password2 = PasswordField(label=_("New Password (confirmation)"), min_length=6,
                                help_text=_("Enter the same password as above, for verification."))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordSetForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user

#------------------------------------------------------------------------------
class PasswordChangeForm(PasswordSetForm):
    """
    A form that lets a user change his/her password by entering
    their old password.
    """
    old_password = PasswordField(label=_("Old Password"), min_length=6)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
        return old_password
PasswordChangeForm.base_fields.keyOrder = ['old_password', 'new_password1', 'new_password2']


#------------------------------------------------------------------------------
class AddApiKeyForm(forms.Form):
    userID = forms.IntegerField(label=_("User ID"))
    apiKey = forms.CharField(label=_("Limited API Key"), min_length=64, max_length=64)
    
    def clean_userID(self):
        """
        Validate that the supplied userID is not already associated to another User.
        """
        if UserAPIKey.objects.filter(userID=self.cleaned_data['userID']):
            raise forms.ValidationError(_("This EVE account is already registered."))
        return self.cleaned_data['userID']
    
    def clean(self):
        cleaned_data = self.cleaned_data
        
        userID = cleaned_data.get("userID")
        apiKey = cleaned_data.get("apiKey")
        
        if userID is not None and apiKey is not None:
            # test if API credentials are valid and if EVE account contains 
            # characters which are members of the corporation
            try:
                self.characters = api.get_account_characters(UserAPIKey(userID=userID, key=apiKey))
                valid_account = False
                for c in self.characters: 
                    exists = Member.objects.filter(characterID=c.characterID).exists()
                    valid_account |= exists and c.is_corped
                if valid_account:
                    ids = [ c.characterID for c in self.characters ]
                    if CharacterOwnership.objects.filter(character__in=ids):
                        self._errors["userID"] = self.error_class([_("A character from this account is already registered by another player")])
                        del cleaned_data["userID"]
                else:
                    self._errors["userID"] = self.error_class([_("This EVE account has no character member of the corporation")])
                    del cleaned_data["userID"]
            except eveapi.Error as e:
                self._errors["userID"] = self.error_class([str(e)])
                self._errors["apiKey"] = self.error_class([str(e)])
                del cleaned_data["userID"]
                del cleaned_data["apiKey"]

        return cleaned_data

#------------------------------------------------------------------------------
class EditApiKeyForm(forms.Form):
    userID = forms.IntegerField(label=_("User ID"), widget=forms.TextInput(attrs={'readonly':'readonly'}))
    apiKey = forms.CharField(label=_("Limited API Key"), min_length=64, max_length=64)
    user = AnonymousUser()
    
    def clean(self):
        cleaned_data = self.cleaned_data
        
        userID = cleaned_data.get("userID")
        apiKey = cleaned_data.get("apiKey")
        
        if userID is not None and apiKey is not None:
            # test if API credentials are valid and if EVE account contains 
            # characters which are members of the corporation
            try:
                self.characters = api.get_account_characters(UserAPIKey(userID=userID, key=apiKey))
                valid_account = False
                for c in self.characters: 
                    exists = Member.objects.filter(characterID=c.characterID).exists()
                    valid_account |= exists and c.is_corped
                if valid_account:
                    ids = [ c.characterID for c in self.characters ]
                    if CharacterOwnership.objects.filter(character__in=ids).exclude(owner=self.user):
                        self._errors["userID"] = self.error_class([_("A character from this account is already registered by another player")])
                        del cleaned_data["userID"]
                else:
                    self._errors["userID"] = self.error_class([_("This EVE account has no character member of the corporation")])
                    del cleaned_data["userID"]
            except eveapi.Error as e:
                self._errors["apiKey"] = self.error_class([str(e)])
                del cleaned_data["apiKey"]

        return cleaned_data

