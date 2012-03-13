'''
Created on 12 Mar 2012

@author: Ajurna
'''

from django.shortcuts import render_to_response
from django.template.context import RequestContext as Ctx

from ecm.apps.eve.models import Type
from ecm.plugins.assets.models import Asset
from ecm.views.decorators import check_user_access


#------------------------------------------------------------------------------
@check_user_access()
def list_bps(request):
    
    return render_to_response('catalog/addbp.html', 
                              Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def get_bps(request):
    bps = Asset.objects.filter(is_original=True)
    out = set()
    for bp in bps:
        try:
            out.add(Type.objects.get(typeID=bp.typeID, category = 9).typeID)
        except Type.DoesNotExist:
            pass
    return out
