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
from django.conf import settings
from django.utils.text import truncate_words
from django.contrib.auth.models import User

from ecm.apps.hr.models import Member
from ecm.apps.common.models import UpdateDate
from ecm.views import template_filters
from ecm.utils.format import print_date
from ecm.utils import db

import logging
logger = logging.getLogger(__name__)



#------------------------------------------------------------------------------
member_table_columns = [
    "name", # default
    "nickname",
    "owner__username",
    "accessLvl",
    "corpDate",
    "lastLogin",
    "location"
]

def get_members(query, first_id, last_id, search_str=None, sort_by=0 , asc=True):

    query = query.select_related(depth=2) # improve performance

    sort_col = member_table_columns[sort_by]
    # SQL hack for making a case insensitive sort
    if sort_by in (0, 1):
        sort_col = sort_col + "_nocase"
        sort_val = db.fix_mysql_quotes('LOWER("%s")' % member_table_columns[sort_by])
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

    query = query[first_id:last_id]

    member_list = []
    for member in query:
        titles = ["Titles"]
        titles.extend(member.titles.values_list("titleName", flat=True))

        memb = [
            member.permalink,
            truncate_words(member.nickname, 5),
            member.owner_permalink,
            member.accessLvl,
            print_date(member.corpDate),
            print_date(member.lastLogin),
            truncate_words(member.location, 5),
            "|".join(titles)
        ]

        member_list.append(memb)

    return total_members, filtered_members, member_list


