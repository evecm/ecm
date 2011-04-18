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

__date__ = "2011 4 6"
__author__ = "diabeteman"

from django import forms
from django.contrib.auth.models import User, AnonymousUser

from captcha.fields import CaptchaField

from ecm.core import api
from ecm.data.common.models import UserAPIKey
from ecm.lib import eveapi
from ecm.data.roles.models import CharacterOwnership
from ecm.view.auth.fields import PasswordField

#------------------------------------------------------------------------------
class AccountCreationForm(forms.Form):

    username = forms.RegexField(label="Username", max_length=30, regex=r'^[\w.@+-]+$',
                                help_text="Required. Less 30 characters. "
                                          "Letters, digits and @/./+/-/_ only.",
                                error_messages = {'invalid': "This field may contain only letters, "
                                                  "numbers and @/./+/-/_ characters."})
    email = forms.EmailField(label="E-Mail address")
    password1 = PasswordField(label="Password", min_length=6)
    password2 = PasswordField(label="Password (confirmation)", min_length=6,
                                help_text="Enter the same password as above, for verification.")
    userID = forms.IntegerField(label="User ID")
    apiKey = forms.CharField(label="Limited API Key", min_length=64, max_length=64)
    captcha = CaptchaField()
    characters = []
    

    

    
    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already in use.
        """
        try:
            User.objects.get(username__iexact=self.cleaned_data['username'])
            raise forms.ValidationError("A user with that username already exists.")
        except User.DoesNotExist:
            return self.cleaned_data['username']
    
    def clean_email(self):
        """
        Validate that the supplied email address is unique for the site.
        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError("This email address is already in use.")
        return self.cleaned_data['email']
    
    def clean_userID(self):
        """
        Validate that the supplied userID is not already associated to another User.
        """
        if UserAPIKey.objects.filter(userID=self.cleaned_data['userID']):
            raise forms.ValidationError("This EVE account is already registered.")
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
                self._errors["password2"] = self.error_class(["Passwords don't match"])
                del cleaned_data["password2"]
            
            # test if API credentials are valid and if EVE account contains 
            # characters which are members of the corporation
            try:
                self.characters = api.get_account_characters(UserAPIKey(userID=userID, key=apiKey))
                if len([ c for c in self.characters if c.is_corped ]) == 0:
                    self._errors["userID"] = self.error_class(["This EVE account has no character member of the corporation"])
                    del cleaned_data["userID"]
                else:
                    ids = [ c.characterID for c in self.characters ]
                    if CharacterOwnership.objects.filter(character__in=ids):
                        self._errors["userID"] = self.error_class(["A character from this account is already registered"])
                        del cleaned_data["userID"]
            except eveapi.Error as e:
                self._errors["userID"] = self.error_class([str(e)])
                self._errors["apiKey"] = self.error_class([str(e)])
                del cleaned_data["userID"]
                del cleaned_data["apiKey"]

        return cleaned_data

#------------------------------------------------------------------------------
class AddApiKeyForm(forms.Form):
    userID = forms.IntegerField(label="User ID")
    apiKey = forms.CharField(label="Limited API Key", min_length=64, max_length=64)
    
    def clean_userID(self):
        """
        Validate that the supplied userID is not already associated to another User.
        """
        if UserAPIKey.objects.filter(userID=self.cleaned_data['userID']):
            raise forms.ValidationError("This EVE account is already registered.")
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
                if len([ c for c in self.characters if c.is_corped ]) == 0:
                    self._errors["userID"] = self.error_class(["This EVE account has no character member of the corporation"])
                    del cleaned_data["userID"]
                else:
                    ids = [ c.characterID for c in self.characters ]
                    if CharacterOwnership.objects.filter(character__in=ids):
                        self._errors["userID"] = self.error_class(["A character from this account is already registered by another player"])
                        del cleaned_data["userID"]
            except eveapi.Error as e:
                self._errors["userID"] = self.error_class([str(e)])
                self._errors["apiKey"] = self.error_class([str(e)])
                del cleaned_data["userID"]
                del cleaned_data["apiKey"]

        return cleaned_data

#------------------------------------------------------------------------------
class EditApiKeyForm(forms.Form):
    userID = forms.IntegerField(label="User ID", widget=forms.TextInput(attrs={'readonly':'readonly'}))
    apiKey = forms.CharField(label="Limited API Key", min_length=64, max_length=64)
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
                if len([ c for c in self.characters if c.is_corped ]) == 0:
                    self._errors["userID"] = self.error_class(["This EVE account has no character member of the corporation"])
                    del cleaned_data["userID"]
                else:
                    ids = [ c.characterID for c in self.characters ]
                    if CharacterOwnership.objects.filter(character__in=ids).exclude(owner=self.user):
                        self._errors["userID"] = self.error_class(["A character from this account is already registered by another player"])
                        del cleaned_data["userID"]
            except eveapi.Error as e:
                self._errors["apiKey"] = self.error_class([str(e)])
                del cleaned_data["apiKey"]

        return cleaned_data

