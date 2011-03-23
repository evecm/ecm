'''
This file is part of ECM

Created on 19 feb. 2011
@author: diabeteman
'''

from ecm.data.corp.models import Corp
from django.core.exceptions import ObjectDoesNotExist

def corporation_name(request):
    try:
        return { "corp_name" : Corp.objects.get(id=1).corporationName }
    except ObjectDoesNotExist:
        return { "corp_name" : "No Corporation" }
