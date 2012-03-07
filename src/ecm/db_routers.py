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

__date__ = '2012 3 7'
__author__ = 'diabeteman'


class ECMDatabaseRouter(object):
    """
    A router to control all database operations on models in ecm
    """

    def db_for_read(self, model, **hints):
        "Point all operations on eve models to 'eve'"
        if model._meta.app_label == 'eve':
            return 'eve'
        return None

    def db_for_write(self, model, **hints):
        "Point all operations on eve models to 'eve'"
        if model._meta.app_label == 'eve':
            return 'eve'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_syncdb(self, db, model):
        "Make sure the eve app only appears on the 'eve' db"
        return model._meta.app_label != 'eve'
