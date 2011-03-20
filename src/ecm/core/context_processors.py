'''
This file is part of ECM

Created on 19 feb. 2011
@author: diabeteman
'''

from ecm.data.corp.models import Corp

def corporation_name(request):
    return {"corp_name" : Corp.objects.all()[0].corporationName}