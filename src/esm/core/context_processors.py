'''
This file is part of ESM

Created on 19 feb. 2011
@author: diabeteman
'''

from esm.data.corp.models import Corp

def corporation_name(request):
    return {"corp_name" : Corp.objects.all()[0].corporationName}