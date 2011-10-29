# Copyright (c) 2011 jerome Vacher
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

__date__ = "2011-04-25"
__author__ = "JerryKhan"

import json,re
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, Http404
from django.core.exceptions import ObjectDoesNotExist
from ecm.data.pos.models import POS
#from ecm.data.common.models import ColorThreshold
from ecm.view.decorators import check_user_access

#------------------------------------------------------------------------------
@check_user_access()
def onePos(request, pos_id):
    try:
        pos = POS.objects.get(itemID=pos_id)
        rex = re.compile(".*\s+([^\s]+)\s+-\s+Moon\s+(\d+)")
        m=rex.match(pos.mlocation)
        if m: mooname = m.group(1)+"-Moon-"+m.group(2)
        else: mooname = 'error in Moon Location Format'
    except ObjectDoesNotExist:
        raise Http404()
    
    data = {
          'pos' : pos
        , 'mooname' : mooname
        , 'fields' : ['-','compo_name','compo_qte','compo_Nb jour','compo_nbHeures','compo_consomation','autres','graph']
    }
    return render_to_response("pos/pos_details.html", data, RequestContext(request))

#------------------------------------------------------------------------------
#@check_user_access()
def fuel_data(request):
    '''Read the fuel detail on bealf ajax request them display a table with content
    '''
    REQ = request.GET if request.method == 'GET' else request.POST
    params = DatatableParams()
    query = POS.objects.filter(location__icontains=request.search)
    fuel_table = []
    for compo in query:
        row = ['compo_icone','compo_name','compo_qte','compo_Nb jour'
               ,'compo_nbHeures','compo_consomation','autres','graph']
        fuel_table.append(row)
    json_data = {
        "sEcho" : request.sEcho,
        #"iTotalRecords" : total_count,  # Number of lines 
        #"iTotalDisplayRecords" : filtered_count,# Number of displayed lines,
        "aaData" : fuel_table
    }
    return HttpResponse(json.dumps(json_data))
