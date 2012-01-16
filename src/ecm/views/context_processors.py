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

__date__ = '2011-02-19'
__author__ = 'diabeteman'


import ecm
from ecm.apps.common.models import user_has_access
from ecm.menu import ECM_MENUS
from ecm.apps.corp.models import Corp

#------------------------------------------------------------------------------
def corporation_name(request):
    """
    Adds the variable {{ corp_name }} to all the templates.
    """
    try:
        return { "corp_name" : Corp.objects.get(id=1).corporationName }
    except Corp.DoesNotExist:
        return { "corp_name" : "No Corporation" }

#------------------------------------------------------------------------------
def version(request):
    """
    Adds the variable {{ ecm_version }} to all the templates.
    """
    return {'ecm_version': ecm.get_version()}

#------------------------------------------------------------------------------
def menu(request):
    """
    Adds the variable {{ user_menu }} to all the templates.

    The menu is composed with items from each ECM app/plugin (see the menu.py files)
    The items are dynamically displayed according to user accesses.
    """
    user_menu = ''
    for menu in ECM_MENUS:
        menu = menu.copy()
        if request.user.is_superuser or user_has_access(request.user, menu['menu_url']):
            menu_items = ''
            for item in menu['menu_items']:
                item = item.copy()
                sub_menu = '\n'.join([ _SUBMENU_HTML % i for i in item['menu_items'] ])
                if sub_menu:
                    sub_menu = '<ul>%s</ul>' % sub_menu
                item['sub_menu'] = sub_menu
                menu_items += _MENU_ITEM_HTML % item

            if menu_items:
                menu_items = '<ul>%s</ul>' % menu_items
            menu['sub_menu'] = menu_items
            user_menu += _MENU_HTML % menu

    return {'user_menu': user_menu}

_MENU_HTML = '''<ul>
  <li>
    <a href="%(menu_url)s">%(menu_title)s</a>
    %(sub_menu)s
  </li>
</ul>
'''
_MENU_ITEM_HTML = '''    <li>
      <a href="%(item_url)s">%(item_title)s</a>
      %(sub_menu)s
    </li>
'''
_SUBMENU_HTML = '      <li><a href="%(item_url)s">%(item_title)s</a></li>'
