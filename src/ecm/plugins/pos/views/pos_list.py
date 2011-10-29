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

import json

from django.db.models.aggregates import Min, Max
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.text import truncate_words

from ecm.data.pos.models import POS, FuelLevel, FUELCOMPOS, FUELID
from ecm.data.common.models import ColorThreshold
from ecm.view import extract_datatable_params
from ecm.view.decorators import check_user_access #???
from ecm.core import utils

from ecm.core.eve import db # For getting invormation on POS type.
from ecm.core.eve import constants as C

# Used to show shorter string for Titles
pos_columns=[
         ['Moon', 'mlocation'] 
       , ['POS Type', 'typeID'] # This is an Hack ... should be better to have the complete type icone.
       , ['Status', 'state']
       , ['Online date','onlineTimeStamp']
       , ['EU','enrichedUranium']   # 44
       , ['O2','oxygen']            # 3683
       , ['MP','mechanicalParts']   # 3689
       , ['Coo','coolant']          # 9832       
       , ['Rob','robotics']         # 9848
       , ['LO','liquidOzone']       # 16273
       , ['HW','heavyWater']        # 16272
       , ['Isot.','']    # WE cannot sort with this column (more complex request maybe for future. (deactivated in js) 17887o,17888n,17889hy,16274he
       , ['Stro.','strontiumClathrates'] # 16275
       , ['hiden','hiden']
       ]

# This table gives the association between the status of the POS and the name of the related Lens Color for display
# Keep in mind the state_texts defined in the POS model.
posColorStatus={'Online':'Green', 'Onlining':'Yellow', 'Reinforced':'RedLight', 'Anchored/Offline':'Blue', 'Unanchorded':'Gray'}

posColorChange={'1':'Green', '2':'Yellow', '3':'RedLight'} # not finished : ideato give a color to the risk of updating in the current hour.

#------------------------------------------------------------------------------
@check_user_access()
def all(request):   
    data = {
          'posViewMode' : 'list'
        , 'fields' : [ f for f,g in pos_columns ]
        , 'colorThresholds' : ColorThreshold.as_json()
        , 'posColorStatus' : json.dumps(posColorStatus)
        #, 'directorAccessLvl' : Member.DIRECTOR_ACCESS_LVL
    }
    return render_to_response("pos/pos_list.html", data, RequestContext(request))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(60 * 60) # 1 hour cache
def all_data(request,b=False):
    '''Read data when table request by Ajax.
    This method takes into account search filter and segmentation table 
    Read the http request (GET methode handling)
    '''
    try:
        request=extract_datatable_params(request)
    except KeyError:
        return HttpResponseBadRequest()

    # Query all by default.
    query = POS.objects.all().select_related(depth=1) # manage cursor on all data

    # Sortting
    sort_col = "%s_nocase" % pos_columns[request.column][1]
    # SQLite hack for making a case insensitive sort
    query = query.extra(select={sort_col : "%s COLLATE NOCASE" % pos_columns[request.column][1]})
    if not request.asc: sort_col = "-" + sort_col
    query = query.extra(order_by=[sort_col])

    # Then get the database content and translate to display table
    # manage the search filter
    displayMode = 'Qtes' # by default
    total_count = 0
    filtered_count = 0
    if request.search:
        if request.search == 'Qtes':   displayMode = 'Qtes'
        elif request.search == 'Days': displayMode = 'Days'
        elif request.search == 'Hours': displayMode = 'Hours'    
        else:
            total_count = query.count()
            query = POS.objects.filter(location__icontains=request.search)
            filtered_count = query.count()
    else:
        total_count = filtered_count = query.count()
    
    pos_table = []
    
    #___________
    def getit(typeid, _in=False):
        try:
            if _in: qlst = pos.fuel_levels.filter(typeID__in=typeid)
            else:   qlst = pos.fuel_levels.filter(typeID=typeid)
            quantity = qlst.latest().quantity
            #print quantity,
            if displayMode == 'Qtes': return quantity
            if _in: cline = pos.fuel_consumptions.filter(typeID__in=typeid).get()
            else:   cline = pos.fuel_consumptions.filter(typeID=typeid).get()
            cons = cline.consumption
            if not cons: return 'No Limit'
            #print cons,
            nbh = int(1.0 *quantity/cons)
            #print nbh,
            if displayMode == 'Hours': return nbh
            nbj = nbh / 24
            if displayMode == 'Days': return nbj
            nbh = nbh % 24
            st =  '%dD%dH' % (nbj,nbh)
            #print st
            return st 
            
        except Exception,msg:
            print "ERROR",msg
            return "ERR"
    #___________
         
    #for pos in query:
    for pos in query[request.first_id:request.last_id]:
        # Query into Fuel table to get last values. for the current POS
        #print pos.Lk2Detail
        try:
            row = [
                 pos.Lk2Detail()
            #, pos.moonID
               , pos.typeID
               , pos.stateText()
               , utils.print_time_min(pos.onlineTimestamp)
               , getit(C.ID_EnrichedUranium)
               , getit(C.ID_Oxygen)
               , getit(C.ID_MechanicalPart)
               , getit(C.ID_Coolant)
               , getit(C.ID_Robotics)
               , getit(C.ID_LiquidOzone)
               , getit(C.ID_HeavyWater)
               , getit(C.ID_ISOTOPS, _in=True)
               , getit(C.ID_strontiumClathrates)
               , pos.isotope
               ]
        except Exception,msg:
            print msg
            row = ['ERR','ERR','ERR','ERR','ERR','ERR','ERR','ERR','ERR','ERR','ERR','ERR','ERR','ERR']
        #print row
        pos_table.append(row)
    
    json_data = {
        "sEcho" : request.sEcho,
        "iTotalRecords" : total_count,  # Number of lines 
        "iTotalDisplayRecords" : filtered_count,# Number of displayed lines,
        "aaData" : pos_table
    }
    return HttpResponse(json.dumps(json_data))


def test(request):
    '''fONCTION DE TEST
    '''
    data = {
          'posViewMode' : 'list'
        , 'fields' : [ f for f,g in pos_columns ]
        #, 'colorThresholds' : ColorThreshold.as_json()
        #, 'directorAccessLvl' : Member.DIRECTOR_ACCESS_LVL
    }
    return render_to_response("pos/pos_list.html", data, RequestContext(request))
