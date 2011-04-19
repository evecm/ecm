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
import json

__date__ = '2010-05-17'
__author__ = 'diabeteman'

import re
import random
import datetime

from django.contrib.auth.models import User
from django.db import models, transaction
from django.conf import settings
from django.utils.hashcompat import sha_constructor

#------------------------------------------------------------------------------
class APIKey(models.Model):
    """
    Represents API credentials that will be used to connect to CCP server
    """
    name = models.CharField(max_length=64)
    userID = models.IntegerField()
    charID = models.IntegerField()
    key = models.CharField(max_length=64)
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __hash__(self):
        return self.userID * 100000000 + self.charID

    def __unicode__(self):
        return u'%s - userID: %d apiKey: %s' % (self.name, self.userID, self.key)

#------------------------------------------------------------------------------
class UserAPIKey(models.Model):
    """
    API credentials used to associate characters to users
    """
    user = models.ForeignKey(User)
    userID = models.IntegerField(primary_key=True)
    key = models.CharField(max_length=64)
    is_valid = models.BooleanField(default=True)
    
    def is_valid_admin_display(self):
        if self.is_valid:
            return "OK"
        else:
            return "Invalid"
    is_valid_admin_display.short_description = "Valid"
    
    def is_valid_html(self):
        if self.is_valid:
            return '<span class="bold ok">API key valid</span>'
        else:
            return '<span class="bold error">API key invalid</span>'

    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __hash__(self):
        return self.userID * 10000 + self.user_id

    def __unicode__(self):
        try:
            return "%s owns %d" % (self.user.username, self.userID)
        except:
            return "%d owns %d" % (self.user_id, self.userID)

#------------------------------------------------------------------------------
class UpdateDate(models.Model):
    """
    Represents the update time of a model's table in the database.
    """
    model_name = models.CharField(primary_key=True, max_length=64)
    update_date = models.DateTimeField()
    prev_update = models.DateTimeField(null=True, blank=True)
    
    def __unicode__(self):
        return "%s updated %s" % (unicode(self.model_name), unicode(self.date))
    
#------------------------------------------------------------------------------
class Outpost(models.Model):
    """
    Conquerable station fetched from CCP servers
    """
    stationID = models.PositiveIntegerField(primary_key=True)
    stationName = models.CharField(max_length=256, default="")
    stationTypeID = models.PositiveIntegerField()
    solarSystemID = models.PositiveIntegerField()
    corporationID = models.PositiveIntegerField()
    corporationName = models.CharField(max_length=256, default="")

    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __hash__(self):
        return self.stationID

    def __unicode__(self):
        return self.stationName


#------------------------------------------------------------------------------
class ColorThreshold(models.Model):
    """
    Thresholds for security access level coloration.
    """
    color = models.CharField(max_length=64)
    threshold = models.IntegerField()
    
    @staticmethod
    def as_json():
        th = ColorThreshold.objects.values("threshold", "color").order_by("threshold")
        return json.dumps(list(th))
    
    def __unicode__(self):
        return unicode("%s -> %d" % (self.color, self.threshold))





#------------------------------------------------------------------------------

SHA1_RE = re.compile('^[a-f0-9]{40}$')

class RegistrationManager(models.Manager):
    def activate_user(self, activation_key):
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                raise ValueError("Activation key not found")
            if not profile.activation_key_expired():
                user = profile.user
                user.is_active = True
                user.save()
                profile.activation_key = self.model.ACTIVATED
                profile.save()
                return user
            else:
                raise UserWarning("Activation key has expired")
        else:
            raise ValueError("Invalid activation key")
    
    def create_inactive_user(self, username, email, password):
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()

        profile = self.create_profile(new_user)

        return new_user, profile
    create_inactive_user = transaction.commit_on_success(create_inactive_user)

    def create_profile(self, user):
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        username = user.username
        if isinstance(username, unicode):
            username = username.encode('utf-8')
        activation_key = sha_constructor(salt+username).hexdigest()
        return self.create(user=user, activation_key=activation_key)
        

class RegistrationProfile(models.Model):

    ACTIVATED = u"ALREADY_ACTIVATED"
    
    user = models.OneToOneField(User)
    activation_key = models.CharField('activation key', max_length=40)
    
    objects = RegistrationManager()
    
    class Meta:
        verbose_name = 'registration profile'
        verbose_name_plural = 'registration profiles'
    
    def __unicode__(self):
        return u"Registration information for %s" % self.user

    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __hash__(self):
        return self.user_id
    
    def activation_key_expired(self):
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == self.ACTIVATED or \
               (self.user.date_joined + expiration_date <= datetime.datetime.now())
    activation_key_expired.boolean = True

