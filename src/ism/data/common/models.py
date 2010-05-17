'''
This file is part of ICE Security Management

Created on 17 mai 2010
@author: diabeteman
'''



from django.db import models



class UpdateDate(models.Model):
    """
    Represents the update time of a model's table in the database.
    """
    model_name = models.CharField(primary_key=True, max_length=64)
    update_date = models.DateTimeField()
    prev_update = models.DateTimeField(null=True, blank=True)
    
    def __unicode__(self):
        return "%s updated %s" % (unicode(self.model_name), unicode(self.date))