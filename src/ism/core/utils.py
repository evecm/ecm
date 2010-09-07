'''
This file is part of ICE Security Management

Created on 16 mai 2010
@author: diabeteman
'''

from ism import settings
from django.contrib.auth.models import Group
from ism.data.common.models import ColorThreshold

try:
    DIRECTOR_GROUP_ID = Group.objects.get(name=settings.DIRECTOR_GROUP_NAME)
except:
    g = Group(name=settings.DIRECTOR_GROUP_NAME).save()
    if g: DIRECTOR_GROUP_ID = g.id
    else: DIRECTOR_GROUP_ID = 1


def print_time(date):
    return date.strftime("%Y-%m-%d %H:%M:%S")

def print_time_min(date):
    return date.strftime("%Y %b %d - %H:%M")

def print_date(date):
    return date.strftime("%Y-%m-%d")

def limit_text_size(text, max_size):
    if len(text) < max_size:
        return text
    else:
        return text[:(max_size - 3)] + "..."


def isDirector(user):
    try:
        g = user.groups.get(name=settings.DIRECTOR_GROUP_NAME)
        if g:
            return True
        else:
            return False
    except:
        return False
    
def getAccessColor(accessLvl):
    colorThresholds = list(ColorThreshold.objects.all().order_by("threshold"))    
    for t in colorThresholds:
        if accessLvl <= t.threshold:
            return t.color
    return colorThresholds[0]
