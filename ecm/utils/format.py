# Copyright (c) 2010-2012 Robin Jarry
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

__date__ = '2010-05-16'
__author__ = 'diabeteman'

import re

#------------------------------------------------------------------------------
def print_time(date):
    try:
        return date.strftime('%H:%M')
    except:
        return date

#------------------------------------------------------------------------------
def print_time_min(date):
    try:
        return date.strftime('%Y %b %d - %H:%M')
    except:
        return date

#------------------------------------------------------------------------------
def print_date(date):
    try:
        return date.strftime('%Y-%m-%d')
    except:
        return date

#------------------------------------------------------------------------------
def print_integer(number, thousand_separator=',', force_sign=False):
    try:
        number = int(round(number))
        negative = number < 0
        number = abs(number)

        result = ''
        while number >= 1000:
            number, r = divmod(number, 1000)
            result = '%s%03d%s' % (thousand_separator, r, result)

        if negative:
            return '- %d%s' % (number, result)
        else:
            return '%s%d%s' % ('+ ' if force_sign else '', number, result)
    except:
        return number

#------------------------------------------------------------------------------
def print_delta(delta):
    try:
        string = ''

        hours, remainder = divmod(delta.seconds, 3600)
        minutes = divmod(remainder, 60)[0]

        if delta.days:
            string += '%d day' % delta.days
            if delta.days > 1:
                string += 's'
            string += ' '
        string += '%dh %dm' % (hours, minutes)

        return string
    except:
        return delta

#------------------------------------------------------------------------------
def print_float(number, thousand_separator=',', decimal_separator='.', force_sign=False):
    try:
        number = float(number)
        decimal_part = ('%.2f' % abs(number - int(number)))[2:]
        return print_integer(int(number), thousand_separator, force_sign) + decimal_separator + decimal_part
    except:
        return number
#------------------------------------------------------------------------------
def print_duration_short(hours):
    if hours / 24 > 0:
        days = hours / 24
        duration = '%dd' % days
        hours = hours % 24
        if hours > 0:
            duration += '&nbsp;%dh' % hours
        return duration
    else:
        return '%dh' % hours

#------------------------------------------------------------------------------
MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
DURATION_UNITS = {
    True: {'day': ' day', 'hour': ' hour', 'min': ' min.', 'sec': ' sec.'}, # verbose
    False: {'day': 'd', 'hour': 'h', 'min': 'm', 'sec': 's'}, # short
}
def print_duration(seconds, verbose=True):
    seconds = int(seconds)
    duration = ''
    days = seconds / DAY
    if days > 0:
        duration += str(days) + '%(day)s'
        if verbose and days > 1:
            duration += 's'
    rest = seconds % DAY
    hours = rest / HOUR
    if hours > 0:
        duration += ' %d' % hours + '%(hour)s'
        if verbose and hours > 1:
            duration += 's'
    rest = rest % HOUR
    minutes = rest / MINUTE
    if minutes > 0:
        duration += ' %d' % minutes + '%(min)s'
    rest = rest % MINUTE
    if rest > 0:
        duration += ' %d' % rest + '%(sec)s'
    if seconds == 0:
        duration = '0'

    duration %= DURATION_UNITS[verbose]
    return duration.strip()


#------------------------------------------------------------------------------
QTY_UNITS = ['K', 'M', 'G', 'T']
def round_quantity(quantity):
    if quantity < 1000 and type(quantity) == type(0):
        return str(quantity)
    else:
        units = QTY_UNITS[:]
        unit = ''
        while quantity >= 1000 and len(units):
            unit = units.pop(0)
            quantity = quantity / 1000.0
        return '%.1f%s' % (quantity, unit)



#------------------------------------------------------------------------------
CAMEL_CASE_RE = re.compile(r'(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))')
MULTI_SPACE_RE = re.compile(r'\s+')
def verbose_name(class_or_function, cap_first=True):
    try:
        name = class_or_function.__name__
        name = CAMEL_CASE_RE.sub(r' \1', name)
        name = name.replace('_', ' ')
        name = MULTI_SPACE_RE.sub(' ', name)
        name = name.lower().strip()
        if cap_first:
            return name[0].upper() + name[1:]
        else:
            return name
    except AttributeError:
        return str(class_or_function)

#------------------------------------------------------------------------------
def print_volume(volume, rounded=False):
    if rounded:
        return '%s m&sup3' % round_quantity(volume)
    else:
        return "%s m&sup3" % print_float(volume)

