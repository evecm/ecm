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


import string
from django import forms
from django.core.exceptions import ValidationError

SPECIAL_CHARS = '!@#$%^&*()[]{}-_+=:;.,<>/"\'~'

class PasswordField(forms.CharField):

    def __init__(self, max_length=None, min_length=None, *args, **kwargs):
        forms.CharField.__init__(self, 
                                 max_length=max_length, 
                                 min_length=max_length, 
                                 widget=forms.PasswordInput, *args, **kwargs)
    
    def validate(self, value):
        super(PasswordField, self).validate(value)
        passwd = set(value)
        if len(passwd) <= self.min_length:
            raise ValidationError('Must be at least %d different characters' % self.min_length)
        if not passwd.intersection(set(string.digits)):
            raise ValidationError('Must contain at least one digit')
        if not (passwd.intersection(set(string.ascii_lowercase)) 
            and passwd.intersection(set(string.ascii_uppercase))):
            raise ValidationError('Must contain lower and upper case characters')
        if not passwd.intersection(set(SPECIAL_CHARS)):
            raise ValidationError('Must contain at least one special character ' + SPECIAL_CHARS)