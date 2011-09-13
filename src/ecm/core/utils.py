# Copyright (c) 2010-2011 Robin Jarry
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

__date__ = "2010-05-16"
__author__ = "diabeteman"


from django.conf import settings



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
def print_integer(number, thousand_separator=",", force_sign=False):
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
        return "%s%d%s" % ("+ " if force_sign else "", number, result)

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
def print_float(number, thousand_separator=",", decimal_separator=".", force_sign=False):
    if type(number) != type(0.0):
        raise TypeError("Parameter must be a float.")
    decimal_part = ("%.2f" % abs(number - int(number)))[2:]
    return print_integer(int(number), thousand_separator, force_sign) + decimal_separator + decimal_part

#------------------------------------------------------------------------------
def get_access_color(accessLvl, colorThresholds):
    for t in colorThresholds:
        if accessLvl <= t.threshold:
            return t.color
    return ""

#------------------------------------------------------------------------------
def fix_mysql_quotes(query):
    """
    MySQL doesn't like double quotes. We replace them by backticks.
    """
    if settings.DATABASES["default"]["ENGINE"] == 'django.db.backends.mysql':
        return query.replace('"', '`')
    else:
        return query


