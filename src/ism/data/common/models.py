'''
This file is part of ICE Security Management

Created on 17 mai 2010
@author: diabeteman
'''



from django.db import models


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
class RefType(models.Model):
    """
    Wallet journal entry transaction type
    """
    
    refTypeID = models.PositiveSmallIntegerField(primary_key=True)
    refTypeName = models.CharField(max_length=64)
    
    def __unicode__(self):
        return unicode(self.refTypeName)
    
    
#------------------------------------------------------------------------------
class Outpost(models.Model):
    stationID = models.PositiveIntegerField(primary_key=True)
    stationName = models.CharField(max_length=256, default="")
    stationTypeID = models.PositiveIntegerField()
    solarSystemID = models.PositiveIntegerField()
    corporationID = models.PositiveIntegerField()
    corporationName = models.CharField(max_length=256, default="")
    
    def __unicode__(self):
        return self.stationName