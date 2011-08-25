


from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseNotFound
from ecm.data.industry.models import CatalogEntry
import json
from django.contrib.auth.decorators import login_required
import time






@login_required
def search_item(request):
    querystring = request.GET.get('q', None)
    if querystring is not None:
        query = CatalogEntry.objects.filter(name__icontains=querystring)
        matches = query.values_list('name', flat=True)
        return HttpResponse('\n'.join(matches))
    else:
        return HttpResponseBadRequest()

@login_required    
def get_item_id(request):
    querystring = request.GET.get('q', None)
    if querystring is not None:
        query = CatalogEntry.objects.filter(name__iexact=querystring)
        if query.exists():
            item = query[0]
            return HttpResponse(json.dumps([item.typeID, item.typeName]))
        else:
            return HttpResponseNotFound()    
    else:
        return HttpResponseBadRequest()