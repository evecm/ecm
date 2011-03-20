'''
This file is part of EVE Corporation Management

Created on 23 mar. 2010
@author: diabeteman
'''


from django.db import models

class APIKey(models.Model):
    
    name = models.CharField(max_length=64)
    userID = models.IntegerField()
    charID = models.IntegerField()
    key = models.CharField(max_length=64)
    
    def __eq__(self, other):
        return (self.userID == other.userID) and (self.charID == other.charID)

    def __unicode__(self):
        return u'%s - userID: %d apiKey: %s' % (self.name, self.userID, self.key)
