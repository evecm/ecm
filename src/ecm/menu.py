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

__date__ = "2011 10 16"
__author__ = "diabeteman"

def compute_menu(plugin):
    menus = []
    for m in plugin.menu:
        m = m.copy()
        m['menu_url'] = '/%s/%s' % (plugin.app_prefix,  m['menu_url'])
        for i in m['menu_items']:
            i['item_url'] = '/%s/%s' % (plugin.app_prefix,  i['item_url'])
            for ii in i['menu_items']:
                ii['item_url'] = '/%s/%s' % (plugin.app_prefix,  ii['item_url'])
        menus.append(m)
    return menus


ECM_MENUS = [
    {'menu_title': 'Home',      'menu_url': '/',            'menu_items': []},
]
import ecm.apps
for app in ecm.apps.LIST:
    ECM_MENUS += compute_menu(app)

import ecm.plugins
for plugin in ecm.plugins.LIST:
    ECM_MENUS += compute_menu(plugin)
