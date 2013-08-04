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

__date__ = "2011 9 10"
__author__ = "diabeteman"

from datetime import timedelta

from django.template.defaultfilters import register

from ecm.utils import _json as json
from ecm.utils.format import print_time_min, print_date, print_duration, print_integer, print_float

#------------------------------------------------------------------------------
@register.filter(name='ecm_date')
def ecm_date(value):
    try:
        return unicode(print_date(value))
    except:
        return unicode(value)

#------------------------------------------------------------------------------
@register.filter(name='ecm_datetime')
def ecm_datetime(value):
    try:
        return unicode(print_time_min(value))
    except:
        return unicode(value)

#------------------------------------------------------------------------------
@register.filter(name='ecm_time')
def ecm_time(value):
    try:
        if isinstance(value, timedelta):
            return unicode(print_date(value))
        else:
            return unicode(print_date(timedelta(seconds=value)))
    except:
        return unicode(value)

#------------------------------------------------------------------------------
@register.filter(name='ecm_duration_long')
def ecm_duration_long(value):
    try:
        return unicode(print_duration(value))
    except:
        return unicode(value)


#------------------------------------------------------------------------------
@register.filter(name='ecm_qty_diff')
def qty_diff_format(value):
    try:
        return unicode(print_integer(value, force_sign=True))
    except:
        return unicode(value)

#------------------------------------------------------------------------------
@register.filter(name='ecm_quantity')
def qty_format(value):
    try:
        return unicode(print_integer(value))
    except:
        return unicode(value)


#------------------------------------------------------------------------------
@register.filter(name='ecm_amount')
def amount_format(value):
    try:
        return unicode(print_float(value, force_sign=True))
    except:
        return unicode(value)

#------------------------------------------------------------------------------
@register.filter(name='ecm_price')
def price_format(value):
    try:
        return unicode(print_float(value))
    except:
        return unicode(value)

#------------------------------------------------------------------------------
@register.filter(name='ecm_absolute')
def absolute_format(value):
    try:
        return unicode(abs(value))
    except:
        return unicode(value)

#------------------------------------------------------------------------------
@register.filter(name='concat')
def concat(value,arg):
    """Merge Strings"""
    try:
        return str(value) + str(arg)
    except (TypeError):
        return ''

#------------------------------------------------------------------------------
@register.inclusion_tag('ecm/datatables.html')
def datatable(table_id, columns, css_class=None, defaults=None, **kwargs):
    """
    table_id
        the html id attribute of the generated table
    columns
        a list of python dicts which should at least contain a 'sTitle' field
        which is the column title.
    defaults
        a dictionary containing default settings for the produced datatables
        those settings can be overwritten by kwargs
    kwargs
        a dictionary containing settings for the produced datatables
        those settings will be outputted as follows:
        
            setting1Name: setting1Value,
            setting2Name: setting2Value,
            setting3Name: setting3Value,
        
    """
    if defaults:
        params_dict = defaults.copy()
    else:
        params_dict = {}
    params_dict.update(kwargs)
    show_header = params_dict.pop('show_header', True)
    show_footer = params_dict.pop('show_footer', True)
    
    datatables_params = [ ('aoColumns', json.dumps(columns)) ]
    
    for key, value in params_dict.items():
        if not key.startswith('fn'):
            # params starting with fn expect function identifiers 
            # and must not be casted to json
            value = json.dumps(value)
        datatables_params.append( (key, value) )
    
    datatables_options = {
        'table_id': table_id,
        'css_class': css_class,
        'columns': columns,
        'show_header': show_header,
        'show_footer': show_footer,
        'empty_css_class': params_dict.get('empty_css_class', 'dataTables_empty'),
        'datatables_params': datatables_params,
    }

    return datatables_options


