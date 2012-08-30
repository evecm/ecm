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

__date__ = '2012 8 30'
__author__ = 'diabeteman'

from datetime import datetime


def ecm_autocast(key, value):
    """
    attempts to cast an XML string to the most probable type.
    """
    
    if value.strip("-").isdigit():
        try:
            return int(value)
        except ValueError:
            pass

    try:
        return float(value)
    except ValueError:
        pass
    
    if len(value) == 19 and value[10] == ' ':
        # it could be a date string
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass

    # couldn't cast. return string unchanged.
    return value


def patch_autocast():
    import eveapi
    eveapi._autocast = ecm_autocast
