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


__date__ = "2010-02-03"
__author__ = "diabeteman"

from django.db.models import Q
from django.utils.text import truncate_words
from django.utils.translation import ugettext as tr

from ecm.apps.hr.models import Member
from ecm.utils.format import print_date
from ecm.utils import db

import logging
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
MEMBERS_COLUMNS = [
    {'sTitle': tr('Name'),         'sWidth': '15%',   'db_field': 'name', },
    {'sTitle': tr('Corp'),         'sWidth': '5%',    'db_field': 'corp', },
    {'sTitle': tr('Player'),       'sWidth': '15%',   'db_field': 'owner__username', },
    {'sTitle': tr('Access Level'), 'sWidth':  '5%',   'db_field': 'accessLvl', },
    {'sTitle': tr('Last Login'),   'sWidth': '10%',   'db_field': 'lastLogin', },
    {'sTitle': tr('Location'),     'sWidth': '20%',   'db_field': 'location', },
    {'sTitle': tr('Ship'),         'sWidth': '15%',   'db_field': 'ship', },
    {'sTitle': tr('Titles'),       'bVisible': False, 'db_field': None, },
]

PLAYERS_COLUMNS = [
    {'sTitle': tr('Name'),         'sWidth': '20%',   'stype': 'html', },
    {'sTitle': tr('Nickname'),     'sWidth': '20%',   'stype': 'string', },
    {'sTitle': tr('Player'),       'sWidth': '15%',   'stype': 'html', },
    {'sTitle': tr('Access Level'), 'sWidth':  '5%',   'stype': 'numeric', },
    {'sTitle': tr('Last Login'),   'sWidth': '10%',   'stype': 'string', },
    {'sTitle': tr('Location'),     'sWidth': '10%',   'stype': 'string', },
    {'sTitle': tr('Ships'),        'sWidth': '20%',   'stype': 'string', },
]

PLAYER_DETAIL_COLUMNS = [
    {'sTitle': tr('Username'),      'sWidth': '20%',   'stype': 'html', },
    {'sTitle': tr('Admin'),         'sWidth': '10%',   'stype': 'html', },
    {'sTitle': tr('EVE Accounts'),  'sWidth': '10%',   'stype': 'string', },
    {'sTitle': tr('Characters'),    'sWidth': '10%',   'stype': 'string', },
    {'sTitle': tr('Groups'),        'sWidth': '10%',   'stype': 'string', },
    {'sTitle': tr('Last Login'),    'sWidth': '20%',   'stype': 'string', },
    {'sTitle': tr('Joined Date'),   'sWidth': '20%',   'stype': 'string', },
]

ACCESS_CHANGES_COLUMNS = [
    {'sTitle': tr('Change'),         'sWidth': '15%',   'stype': 'string', },
    {'sTitle': tr('Title/Role'),     'sWidth': '50%',   'stype': 'html', },
    {'sTitle': tr('Date'),           'sWidth': '25%',   'stype': 'string', },
]

ROLES_COLUMNS = [
    {'sTitle': tr('Role Name'),      'sWidth': '30%',   'stype': 'html',    'bSortable': False, },
    {'sTitle': tr('Description'),    'sWidth': '55%',   'stype': 'string',  'bSortable': False, },
    {'sTitle': tr('Access Level'),   'sWidth': ' 5%',   'stype': 'numeric', 'bSortable': False, },
    {'sTitle': tr('Members'),        'sWidth':  '5%',   'stype': 'numeric', 'bSortable': False, },
    {'sTitle': tr('Titles'),         'sWidth': ' 5%',   'stype': 'numeric', 'bSortable': False, },
    {'bVisible': False, },
    {'bVisible': False, },
    {'bVisible': False, },
]

TITLES_COLUMNS = [
    {'sTitle': tr('Title Name'),     'sWidth': '40%',   'stype': 'html', },
    {'sTitle': tr('Access Level'),   'sWidth': '20%',   'stype': 'numeric', 'bSearchable': False, },
    {'sTitle': tr('Members'),        'sWidth': '10%',   'stype': 'html',    'bSearchable': False, 'bSortable': False, },
    {'sTitle': tr('Role Count'),     'sWidth': '10%',   'stype': 'numeric', 'bSearchable': False, 'bSortable': False, },
    {'sTitle': tr('Last Modified'),  'sWidth': '20%',   'stype': 'string',  'bSearchable': False, 'bSortable': False, },
]

TITLES_DETAIL_COLUMNS = [
    {'sTitle': tr('Role'),           'sWidth': '50%',   'stype': 'html',    'bSortable': False, },
    {'sTitle': tr('Category'),       'sWidth': '30%',   'stype': 'html',    'bSortable': False, },
    {'sTitle': tr('Access Level'),   'sWidth': '20%',   'stype': 'numeric', 'bSortable': False, },
]

TITLES_MOD_COLUMNS = [
    {'sTitle': tr('Change'),            'sWidth': '10%',   'stype': 'html',    'bSortable': False, },
    {'sTitle': tr('Role'),              'sWidth': '40%',   'stype': 'html',    'bSortable': False, },
    {'sTitle': tr('Category'),          'sWidth': '25%',   'stype': 'html',    'bSortable': False, },
    {'sTitle': tr('Modification Date'), 'sWidth': '25%',   'stype': 'numeric', 'bSortable': False, },
]

def get_members(query, first_id, last_id, search_str=None, sort_by=0 , asc=True, format=None):

    query = query.select_related(depth=2) # improve performance

    sort_col = MEMBERS_COLUMNS[sort_by]['db_field']
    # SQL hack for making a case insensitive sort
    if sort_by in (0, 1):
        sort_col = sort_col + "_nocase"
        sort_val = db.fix_mysql_quotes('LOWER("%s")' % MEMBERS_COLUMNS[sort_by]['db_field'])
        query = query.extra(select={ sort_col : sort_val })

    
    if not asc: sort_col = "-" + sort_col
    query = query.extra(order_by=([sort_col]))

    if search_str:
        total_members = query.count()
        search_args = Q(name__icontains=search_str) | Q(nickname__icontains=search_str)

        if "DIRECTOR".startswith(search_str.upper()):
            search_args = search_args | Q(accessLvl=Member.DIRECTOR_ACCESS_LVL)

        query = query.filter(search_args)
        filtered_members = query.count()
    else:
        total_members = filtered_members = query.count()
        
    member_list = []
    if format == 'csv':
        for member in query:
            member_list.append([
                member.name,
                member.nickname,
                member.corp or '-',
                member.owner,
                member.lastLogin,
                member.location,
                member.ship or '(docked)',
                member.accessLvl,
                ' '.join([ t.titleName for t in member.titles.all() ]),
            ])
    else:
        for member in query[first_id:last_id]:
            titles = ["Titles"]
            titles.extend(member.titles.values_list("titleName", flat=True))
            
            if member.corp:
                corp = '<span title="%s">%s</span>' % (member.corp, member.corp.ticker)
            else:
                corp = '-'
            
            memb = [
                member.permalink,
                corp,
                member.owner_permalink,
                member.accessLvl,
                print_date(member.lastLogin),
                truncate_words(member.location, 5),
                member.ship or '(docked)',
                "|".join(titles)
            ]
    
            member_list.append(memb)

    return total_members, filtered_members, member_list


