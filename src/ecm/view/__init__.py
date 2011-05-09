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

__date__ = "2010-02-03"
__author__ = "diabeteman"

from django.db.models import Q
from django.utils.text import truncate_words

from ecm.data.roles.models import Member, CharacterOwnership
from ecm.core import utils
from ecm.data.common.models import UpdateDate

#------------------------------------------------------------------------------
def getScanDate(model_name):
    try:
        date = UpdateDate.objects.get(model_name=model_name) 
        return utils.print_time_min(date.update_date)
    except UpdateDate.DoesNotExist:
        return "<no data>"

#------------------------------------------------------------------------------
def extract_datatable_params(request):
    REQ = request.GET if request.method == 'GET' else request.POST
    request.first_id = int(REQ["iDisplayStart"])
    request.length = int(REQ["iDisplayLength"])
    request.last_id = request.first_id + request.length - 1
    request.search = REQ["sSearch"]
    request.sEcho = int(REQ["sEcho"])
    request.column = int(REQ["iSortCol_0"])
    request.asc = (REQ["sSortDir_0"] == "asc")

#------------------------------------------------------------------------------
member_table_columns = [
    "name", # default
    "nickname",
    "user", # not sortable
    "accessLvl",
    "corpDate",
    "lastLogin",
    "location"
]
def get_members(query, first_id, last_id, search_str=None, sort_by=0 , asc=True):

    sort_col = member_table_columns[sort_by]
    # SQL hack for making a case insensitive sort
    if sort_by in [0, 1]:
        sort_col = sort_col + "_nocase"
        query = query.extra(select={sort_col : 'LOWER("%s")' % member_table_columns[sort_by]})
    if not asc: sort_col = "-" + sort_col
    query = query.extra(order_by=[sort_col])
    
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
            member.as_html(),
            truncate_words(member.nickname, 5),
            member.owner_as_html(),
            member.accessLvl,
            utils.print_date(member.corpDate),
            utils.print_date(member.lastLogin),
            truncate_words(member.location, 5),
            "|".join(titles)
        ] 

        member_list.append(memb)
    
    return total_members, filtered_members, member_list
