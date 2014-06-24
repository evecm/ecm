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

NAME = 'common'

TASKS = [
    {
        'function' : 'ecm.apps.common.tasks.users.cleanup_unregistered_users',
        'priority' : 0,
        'frequency' : 1,
        'frequency_units' : 60 * 60 * 24, # day
    }, {
        'function' : 'ecm.apps.common.tasks.outposts.update',
        'priority' : 1000,
        'frequency' : 1,
        'frequency_units' : 60 * 60 * 24, # day
    },
]

URL_PERMISSIONS = [
    r'^/editmotd/$',
]

SETTINGS = {
    'common_api_keyID': 0,
    'common_api_vCode': '',
    'common_api_characterID': 0,
    'common_admin_username': 'admin',
    'common_cron_username': 'cron',
}
