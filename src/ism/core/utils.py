'''
This file is part of ICE Security Management

Created on 16 mai 2010
@author: diabeteman
'''

from ism import settings
from django.contrib.auth.models import Group

try:
    DIRECTOR_GROUP_ID = Group.objects.get(name=settings.DIRECTOR_GROUP_NAME)
except:
    g = Group(name=settings.DIRECTOR_GROUP_NAME).save()
    if g: DIRECTOR_GROUP_ID = g.id
    else: DIRECTOR_GROUP_ID = 1

#------------------------------------------------------------------------------
def print_time(date):
    return date.strftime("%Y-%m-%d %H:%M:%S")

#------------------------------------------------------------------------------
def print_time_min(date):
    return date.strftime("%Y %b %d - %H:%M")

#------------------------------------------------------------------------------
def print_date(date):
    return date.strftime("%Y-%m-%d")

#------------------------------------------------------------------------------
def limit_text_size(text, max_size):
    if len(text) < max_size:
        return text
    else:
        return text[:(max_size - 3)] + "..."

#------------------------------------------------------------------------------
def print_integer(number, thousand_separator=" "):
    if type(number) not in [type(0), type(0L)]:
        raise TypeError("Parameter must be an integer.")
    
    number = abs(number)

    result = ''
    while number >= 1000:
        number, r = divmod(number, 1000)
        result = "%s%03d%s" % (thousand_separator, r, result)
    
    return "%d%s" % (number, result)

#------------------------------------------------------------------------------
def print_quantity(number, thousand_separator=" "):
    if type(number) not in [type(0), type(0L)]:
        raise TypeError("Parameter must be an integer.")
    
    negative = number < 0
    number = abs(number)

    result = ''
    while number >= 1000:
        number, r = divmod(number, 1000)
        result = "%s%03d%s" % (thousand_separator, r, result)
    
    if negative:
        return "- %d%s" % (number, result)
    else:
        return "+ %d%s" % (number, result)



#------------------------------------------------------------------------------
def print_float(number, thousand_separator=" ", decimal_separator=","):
    if type(number) != type(0.0):
        raise TypeError("Parameter must be a float.")
    decimal_part = ("%.2f" % abs(number - int(number)))[2:]
    return print_integer(int(number), thousand_separator) + decimal_separator + decimal_part

#------------------------------------------------------------------------------
def isDirector(user):
    try:
        g = user.groups.get(name=settings.DIRECTOR_GROUP_NAME)
        if g:
            return True
        else:
            return False
    except:
        return False

#------------------------------------------------------------------------------
def getAccessColor(accessLvl, colorThresholds):
    for t in colorThresholds:
        if accessLvl <= t.threshold:
            return t.color
    return colorThresholds[0].color


def merge_lists(list_a, list_b, attribute=None):
    merged_list = []
    a = list_a[:]
    b = list_b[:]
    
    if attribute:
        while a and b:
            if a[-1].__getattr__(attribute) <= b[-1].__getattr__(attribute):
                merged_list.insert(0, a.pop())
            else:
                merged_list.insert(0, b.pop())
    else:
        while a and b:
            if a[-1] <= b[-1]:
                merged_list.insert(0, a.pop())
            else:
                merged_list.insert(0, b.pop())
    
    merged_list += a if a else b
    
    return merged_list
