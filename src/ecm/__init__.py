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
__author__ = "diabeteman"

__date__ = "2011-05-17"

TIMESTAMP = "%(timestamp)s"
VERSION = (2, 0, 0)
__version_str__ = '.'.join(map(str, VERSION))

def get_version():
    return __version_str__

def get_full_version():
    return  get_version() + '.' + TIMESTAMP
