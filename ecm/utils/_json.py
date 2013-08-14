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
import json
try:
    JSON_ENCODER = json.encoder.JSONEncoder
except AttributeError:
    JSON_ENCODER = json.JSONEncoder

#------------------------------------------------------------------------------
def load(fp, object_hook=None, **kw):
    object_hook = object_hook or __datetime_json_decoder
    return json.load(fp, object_hook=object_hook, **kw)

#------------------------------------------------------------------------------
def dump(obj, fp, cls=None, **kw):
    cls = cls or DatetimeJSONEncoder
    return json.dump(obj, fp, cls=cls, **kw)

#------------------------------------------------------------------------------
def loads(s, object_hook=None, **kw):
    object_hook = object_hook or __datetime_json_decoder
    return json.loads(s, object_hook=object_hook, **kw)

#------------------------------------------------------------------------------
def dumps(obj, cls=None, **kw):
    cls = cls or DatetimeJSONEncoder
    return json.dumps(obj, cls=cls, **kw)

#------------------------------------------------------------------------------
DATE_PATTERN = '%Y-%m-%d_%H-%M-%S'

class DatetimeJSONEncoder(JSON_ENCODER):

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime(DATE_PATTERN)
        else:
            return JSON_ENCODER.default(self, obj)

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
