# The MIT License - EVE Corporation Management
# 
# Copyright (c) 2010 Robin Jarry
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

'''
This file is part of ECM

Created on 19 feb. 2011
@author: diabeteman
'''

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
    
