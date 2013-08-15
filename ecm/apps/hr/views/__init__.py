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
from django.utils.translation import ugettext as tr

from ecm.apps.hr.models import Member
from ecm.utils.format import print_date
from ecm.utils import db

import logging
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
MEMBERS_COLUMNS = [
    {'sTitle': tr('Name'),         'sWidth': '15%',   'db_field': 'name', },
    {'sTitle': tr('Corp'),         'sWidth': '5%',    'db_field': 'corp__corporationName', },
    {'sTitle': tr('Player'),       'sWidth': '15%',   'db_field': 'owner__username', },
    {'sTitle': tr('Access Level'), 'sWidth':  '5%',   'db_field': 'accessLvl', },
    {'sTitle': tr('Last Login'),   'sWidth': '10%',   'db_field': 'lastLogin', },
    {'sTitle': tr('Location'),     'sWidth': '20%',   'db_field': 'location', },
    {'sTitle': tr('Ship'),         'sWidth': '15%',   'db_field': 'ship', },
    {'sTitle': tr('Titles'),       'bVisible': False, 'db_field': None, },
]

def get_members(query, first_id, last_id, search_str=None, sort_by=0, asc=True, for_csv=False):

    query = query.select_related(depth=2) # improve performance

    sort_col = MEMBERS_COLUMNS[sort_by]['db_field']
    # SQL hack for making a case insensitive sort
    if sort_by == 0:
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
    if for_csv:
        for member in query:
            member_list.append([
                member.name,
                member.nickname,
                member.corp or '-',
                member.owner,
                member.lastLogin,
                member.dotlan_location,
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
                member.dotlan_location,
                member.ship or '(docked)',
                "|".join(titles)
            ]
    
            member_list.append(memb)

    return total_members, filtered_members, member_list


