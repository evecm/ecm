'''
This file is part of EVE Corporation Management

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
class Outpost(models.Model):
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
    
    color = models.CharField(max_length=64)
    threshold = models.IntegerField()
    
    def __unicode__(self):
        return unicode("%s -> %d" % (self.color, self.threshold))
