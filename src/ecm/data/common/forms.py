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
from ecm.data.common.fields import MultiIntegerField
from ecm.data.roles.models import Member

__date__ = "2011 4 6"
__author__ = "diabeteman"

from django import forms
from ecm.core import api
from ecm.data.corp.models import Corp
from ecm.data.common.models import UserAPIKey
from ecm.lib import eveapi


class UserApiKeyForm(forms.Form):
    userID = forms.IntegerField(label="User ID")
    apiKey = forms.CharField(label="API Key", min_length=64, max_length=64)
    

    
    def clean(self):
        cleaned_data = self.cleaned_data
        
        userID = cleaned_data.get("userID")
        apiKey = cleaned_data.get("apiKey")
        
        if userID and apiKey:
            self.api = UserAPIKey(userID=userID, key=apiKey)
            
            try:
                conn = api.connect_user(user_api=self.api)
                resp = conn.account.Characters()
                
                corp = Corp.objects.get(id=1)

                self.characters = []
                for char in resp.characters:
                    c = Character()
                    c.name = char.name
                    c.characterID = char.characterID
                    c.corporationID = char.corporationID
                    c.corporationName = char.corporationName
                    c.is_corped = char.corporationID == corp.corporationID
                    self.characters.append(c)
                    
                if not corp.corporationID in [ char.corporationID for char in self.characters ]:
                    raise forms.ValidationError("This account has no character member of %s" % corp.corporationName)
                    
            except eveapi.Error as e:
                raise forms.ValidationError(str(e))

        return cleaned_data

class AccountCreationForm(forms.Form):
    userID = forms.IntegerField(label="User ID")
    apiKey = forms.CharField(label="API Key", min_length=64, max_length=64)
    character_ids = MultiIntegerField(widget=forms.HiddenInput)
    main_character_id = forms.IntegerField(label="Main Character")

    username  = forms.SlugField(label="Login Name")
    email = forms.EmailField(label="E-Mail address")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Password (repeat)")
    
    
    def clean(self):
        cleaned_data = self.cleaned_data
        
        userID = cleaned_data.get("userID")
        apiKey = cleaned_data.get("apiKey")
        character_ids = cleaned_data.get("character_ids")
        main_character_id = cleaned_data.get("main_character_id")
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        
        if not None in (userID, apiKey, character_ids, main_character_id, 
                        username, email, password1, password2):
            # test if passwords don't match
            if not password1 == password2:
                raise forms.ValidationError("Passwords must match")
            try:
                chars = list(Member.objects.filter(characterID__in=character_ids))
                alt_chars = []
                main_char = None
                
                while len(chars):
                    if chars[0].characterID == main_character_id:
                        main_char = chars.pop(0)
                    else:
                        alt_chars.append(chars.pop(0))
            
            except Exception as e:
                raise forms.ValidationError(str(e))

        return cleaned_data

class Character:
    name = ""
    characterID = 0
    corporationID = 0
    corporationName = "No Corporation"
    is_corped = False
