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


NAME = 'hr'

TASKS = [
    {
        'function' : 'ecm.apps.hr.tasks.membertrack.update',
        'priority' : 50,
        'frequency' : 2,
        'frequency_units' : 3600, # hour
    }, {
        'function' : 'ecm.apps.hr.tasks.membersecu.update',
        'priority' : 20,
        'frequency' : 2,
        'frequency_units' : 3600, # hour
    }, {
        'function' : 'ecm.apps.hr.tasks.titles.update',
        'priority' : 10,
        'frequency' : 6,
        'frequency_units' : 3600, # hour
    }, {
        'function' : 'ecm.apps.hr.tasks.users.update_all_character_associations.update',
        'priority' : 5,
        'frequency' : 1,
        'frequency_units' : 86400, # day
    }, {
        'function' : 'ecm.apps.hr.tasks.users.update_all_users_accesses',
        'priority' : 1,
        'frequency' : 2,
        'frequency_units' : 3600, # hour
    },
]
