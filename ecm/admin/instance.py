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

__date__ = '2012 3 24'
__author__ = 'diabeteman'

from ecm.admin.util import get_logger

#------------------------------------------------------------------------------
class ECMInstance(object):

    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.logger = get_logger()

    def create(self, options):
        pass

    def destroy(self):
        pass

    def update(self):
        pass

    def upgrade(self):
        pass

    def manage(self, *args, **kwargs):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def restart(self):
        pass