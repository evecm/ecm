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

__date__ = "2011 9 5"
__author__ = "diabeteman"

from django.template.defaultfilters import register

from ecm.core import utils

#------------------------------------------------------------------------------
@register.filter(name='ecm_date')
def date_format(value):
    try:
        return unicode(utils.print_date(value))
    except:
        return unicode(value)

#------------------------------------------------------------------------------
@register.filter(name='ecm_datetime')
def datetime_format(value):
    try:
        return unicode(utils.print_time_min(value))
    except:
        return unicode(value)

#------------------------------------------------------------------------------
@register.filter(name='ecm_qty_diff')
def qty_diff_format(value):
    try:
        return unicode(utils.print_integer(int(value), force_sign=True))
    except:
        return unicode(value)

#------------------------------------------------------------------------------
@register.filter(name='ecm_quantity')
def qty_format(value):
    try:
        return unicode(utils.print_float(int(value)))
    except:
        return unicode(value)


#------------------------------------------------------------------------------
@register.filter(name='ecm_amount')
def amount_format(value):
    try:
        return unicode(utils.print_float(float(value), force_sign=True))
    except:
        return unicode(value)

#------------------------------------------------------------------------------
@register.filter(name='ecm_price')
def price_format(value):
    try:
        return unicode(utils.print_float(float(value)))
    except:
        return unicode(value)
