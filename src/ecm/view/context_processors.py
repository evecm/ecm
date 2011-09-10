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
import ecm

__date__ = '2011-02-19'
__author__ = 'diabeteman'


from ecm.data.common.models import user_has_access
from ecm.urls import ecm_menus
from ecm.data.corp.models import Corp

def corporation_name(request):
    try:
        return { "corp_name" : Corp.objects.get(id=1).corporationName }
    except Corp.DoesNotExist:
        return { "corp_name" : "No Corporation" }


menu_html = '''<ul>
  <li>
    <a href="%(menu_url)s">%(menu_title)s</a>
    %(sub_menu)s
  </li>
</ul>
'''

submenu_item_html = '<li><a href="%(item_url)s">%(item_title)s</a></li>'

def menu(request):
    user_menu = ''
    for menu in ecm_menus:
        menu = menu.copy()
        if request.user.is_superuser or user_has_access(request.user, menu['menu_url']):
            sub_menu = '\n'.join([submenu_item_html % item for item in menu['menu_items']])
            if sub_menu:
                sub_menu = '<ul>%s</ul>' % sub_menu
            menu['sub_menu'] = sub_menu
            user_menu += menu_html % menu
    return {'user_menu': user_menu}
    
def version(request):
    return {'ecm_version': ecm.version}

