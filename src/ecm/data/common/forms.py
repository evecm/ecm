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
from ecm.core import api
from ecm.data.corp.models import Corp
from ecm.data.common.models import UserAPIKey
from ecm.lib import eveapi


class UserSignupForm(forms.Form):
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

class Character:
    name = ""
    characterID = 0
    corporationID = 0
    corporationName = "No Corporation"
    is_corped = False
