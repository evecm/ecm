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

__date__ = "2012 08 09"
__author__ = "ajurna"


from django.utils.translation import ugettext as tr, ugettext_lazy as tr_lazy, ugettext_noop as tr_noop


NAME = 'alerts'

#MENUS = [
#    {'title': tr_lazy('Alert System'),   'url': 'alerts/',     'items': []},
#]

TASKS = [
    {
        'function': 'ecm.apps.alerts.views.task',
        'priority': 50,
        'frequency': 6,
        'frequency_units': 3600, # hour
    }
]

URL_PERMISSIONS = [
    r'^/alerts/.*$',
]



