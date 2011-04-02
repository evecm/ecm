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

__date__ = "2010-05-16"
__author__ = "diabeteman"



from ecm import settings
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
def print_delta(delta):
    string = ""
    
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = divmod(remainder, 60)[0]
    
    if delta.days:  
        string += "%d day" % delta.days
        if delta.days > 1: 
            string += "s"
        string += " "
    string += "%dh %dm" % (hours, minutes)
    
    return string

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
def has_change_permission(user, model):
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


def merge_lists(list_a, list_b, ascending=True, attribute=None):
    merged_list = []
    a = list(list_a)
    b = list(list_b)
                 
    if attribute:
        if ascending:
            while a and b:
                if a[0].__getattr__(attribute) < b[0].__getattr__(attribute):
                    merged_list.append(a.pop(0))
                else:
                    merged_list.append(b.pop(0))
        else:
            while a and b:
                if a[0].__getattr__(attribute) > b[0].__getattr__(attribute):
                    merged_list.append(a.pop(0))
                else:
                    merged_list.append(b.pop(0))
    else:
        if ascending:
            while a and b:
                if a[0] < b[0]:
                    merged_list.append(a.pop(0))
                else:
                    merged_list.append(b.pop(0))
        else:
            while a and b:
                if a[0] > b[0]:
                    merged_list.append(a.pop(0))
                else:
                    merged_list.append(b.pop(0))
    
    merged_list += a or b
    
    return merged_list
