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
from django.contrib.auth.models import User

'''
This file is part of EVE Corporation Management

Created on 17 mai 2010
@author: diabeteman
'''



from django.db import models

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
        return (self.userID == other.userID) and (self.charID == other.charID)

    def __unicode__(self):
        return u'%s - userID: %d apiKey: %s' % (self.name, self.userID, self.key)

#------------------------------------------------------------------------------
class UserAPIKey(models.Model):
    """
    API credentials used to associate characters to users
    """
    user = models.ForeignKey(User)
    userID = models.IntegerField()
    key = models.CharField(max_length=64)
    is_valid = models.BooleanField(default=True)
    
    def is_valid_admin_display(self):
        if self.is_valid:
            return "OK"
        else:
            return "Invalid"
    is_valid_admin_display.short_description = "Valid"

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
    
    def __unicode__(self):
        return self.stationName


#------------------------------------------------------------------------------
class ColorThreshold(models.Model):
    """
    Thresholds for security access level coloration.
    """
    color = models.CharField(max_length=64)
    threshold = models.IntegerField()
    
    def __unicode__(self):
        return unicode("%s -> %d" % (self.color, self.threshold))
