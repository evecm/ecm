'''
This file is part of ICE Security Management

Created on 21 mai 2010
@author: diabeteman
'''
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page


from ism.core.db import resolveLocationName, resolveTypeName
from ism.data.common.models import UpdateDate
from ism.data.assets.models import DbAsset
from ism.data.corp.models import Hangar


@login_required
@cache_page(60 * 15) # 15 minutes cache
def stations(request):
    data = {  'station_list' : getStations(),
                'scan_date' : getScanDate() }
    return render_to_response("stations.html", data, context_instance=RequestContext(request))

@login_required
@cache_page(60 * 15) # 15 minutes cache
def station_assets(request, stationID):
    data = {  'item_list' : getStationItems(int(stationID)),
               'station_name' : resolveLocationName(int(stationID)),
                'scan_date' : getScanDate() }
    return render_to_response("station_details.html", data, context_instance=RequestContext(request))



def getStations():
    raw_list = DbAsset.objects.raw("SELECT itemID, locationID, count(*) AS items FROM assets_dbasset GROUP BY locationID;")
    class S: 
        locationID = 0
        name = None
        items = 0
    station_list = []
    for s in raw_list:
        station = S()
        station.locationID = s.locationID
        station.name = resolveLocationName(s.locationID)
        station.items = s.items
        station_list.append(station)
    return station_list

def getStationItems(stationID):
    item_list = DbAsset.objects.filter(locationID=stationID)
    for i in item_list:
        i.name = resolveTypeName(i.typeID)
        i.hangar = Hangar.objects.get(hangarID=i.hangarID).name
    return item_list
    
def getScanDate():
    date = UpdateDate.objects.get(model_name=DbAsset.__name__) 
    return date.update_date