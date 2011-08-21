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
from django.http import HttpResponse

__date__ = "2011 8 19"
__author__ = "diabeteman"


import json
from datetime import datetime

from django.template.context import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from ecm.core import utils
from ecm.data.industry.models import Order


#------------------------------------------------------------------------------

def details(request, order_id):
    order = get_object_or_404(Order, id=int(order_id))
    
    logs = list(order.logs.all().order_by('date'))
    try:
        creationDate = utils.print_time_min(logs[0].date)
    except IndexError:
        creationDate = utils.print_time_min(datetime.now())
    try:
        lastModifiedDate = utils.print_time_min(logs[-1].date)
    except IndexError:
        lastModifiedDate = utils.print_time_min(datetime.now())

    data = {'order' : order,
       'creationDate' : creationDate,
       'lastModifiedDate':lastModifiedDate}
    
    return render_to_response('industry/order_details.html', data, RequestContext(request))

def rows_data(request, order_id):
    order = get_object_or_404(Order, id=int(order_id))
    rows = []
    
    for row in order.rows.all():
        rows.append([
            row.item.typeName,
            row.quantity,
            row.quote,
            '<a href="/industry/row/%d/delete&next=/industry/order/%s">Remove</a>' % (row.id, order.id)
        ])
    
    return HttpResponse(json.dumps(rows))
    


