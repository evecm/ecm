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

__date__ = "2011 4 6"
__author__ = "diabeteman"


import string

from django.conf import settings
from django import forms
from django.core.exceptions import ValidationError

SPECIAL_CHARS = '!@#$%^&*()[]{}-_+=:;.,<>/"\'~'

class PasswordField(forms.CharField):

    def __init__(self, max_length=None, min_length=None, *args, **kwargs):
        if min_length is None:
            min_length = settings.PASSWD_MIN_LENGTH
        forms.CharField.__init__(self, 
                                 max_length=max_length, 
                                 min_length=max_length, 
                                 widget=forms.PasswordInput, *args, **kwargs)
    
    def validate(self, value):
        super(PasswordField, self).validate(value)
        passwd = set(value)
        if len(passwd) <= self.min_length:
            raise ValidationError('Must be at least %d different characters' % self.min_length)
        if settings.PASSWD_FORCE_DIGITS and not passwd.intersection(set(string.digits)):
            raise ValidationError('Must contain at least one digit')
        if settings.PASSWD_FORCE_LETTERS and not passwd.intersection(set(string.ascii_letters)):
            raise ValidationError('Must contain at least one letter')
        if settings.PASSWD_FORCE_SPECIAL_CHARS and not passwd.intersection(set(SPECIAL_CHARS)):
            raise ValidationError('Must contain at least one special character ' + SPECIAL_CHARS)
