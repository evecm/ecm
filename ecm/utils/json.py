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

__date__ = '2012-09-01'
__author__ = 'diabeteman'

import re
from datetime import datetime
import django.utils.simplejson as JSON

#------------------------------------------------------------------------------
def loads(s, encoding=None, cls=None, object_hook=None, parse_float=None,
          parse_int=None, parse_constant=None, object_pairs_hook=None,
          use_decimal=False, **kw):
    
    object_hook = object_hook or __datetime_json_decoder
    
    return JSON.loads(s, encoding, cls, object_hook, parse_float, parse_int, parse_constant, 
                      object_pairs_hook, use_decimal)
  
#------------------------------------------------------------------------------  
def dumps(obj, skipkeys=False, ensure_ascii=True, check_circular=True,
          allow_nan=True, cls=None, indent=None, separators=None,
          encoding='utf-8', default=None, use_decimal=True,
          namedtuple_as_object=True, tuple_as_array=True,
          bigint_as_string=False, sort_keys=False, item_sort_key=None,
          **kw):

    cls = cls or DatetimeJSONEncoder

    return JSON.dumps(obj, skipkeys, ensure_ascii, check_circular, allow_nan, cls, 
                      indent, separators, encoding, default)#, use_decimal, namedtuple_as_object, 
                      #tuple_as_array, bigint_as_string, sort_keys, item_sort_key)
                      #Fix for too many args to dumps.
    
#------------------------------------------------------------------------------
DATE_PATTERN = '%Y-%m-%d_%H-%M-%S'
class DatetimeJSONEncoder(JSON.JSONEncoder):
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime(DATE_PATTERN)
        else:
            print type(obj)
            JSON.JSONEncoder.default(self, obj)

#------------------------------------------------------------------------------
DATE_RE = re.compile('\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}')
def __datetime_json_decoder(obj_dict):
    
    for key, val in obj_dict.items():
        if isinstance(val, basestring) and DATE_RE.search(val):
            try:
                obj_dict[key] = datetime.strptime(val, DATE_PATTERN)
            except ValueError:
                pass

    return obj_dict
