


from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseNotFound
from ecm.data.industry.models import CatalogEntry
import json
from django.contrib.auth.decorators import login_required
import time






@login_required
def search_item(request):
    querystring = request.GET.get('q', None)
    try:
        limit = int(request.GET.get('limit', "10"))
    except ValueError:
        limit = 10
    if querystring is not None:
        query = CatalogEntry.objects.filter(typeName__icontains=querystring).order_by('typeName')
        matches = query[:limit].values_list('typeName', flat=True)
        return HttpResponse( '\n'.join(matches) )
    else:
        return HttpResponseBadRequest()

@login_required    
def get_item_id(request):
    querystring = request.GET.get('q', None)
    if querystring is not None:
        query = CatalogEntry.objects.filter(typeName__iexact=querystring)
        if query.exists():
            item = query[0]
            return HttpResponse( json.dumps( [item.typeID, item.typeName] ) )
        else:
            return HttpResponseNotFound()    
    else:
        return HttpResponseBadRequest()