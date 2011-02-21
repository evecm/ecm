'''
This file is part of ICE Security Management

Created on 16 mai 2010
@author: diabeteman
'''


from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.core.exceptions import ObjectDoesNotExist

from ism.data.corp.models import Corp

import re

SHOWINFO_PATTERN = re.compile(r"showinfo:1383//(\d+)", re.IGNORECASE + re.DOTALL)

#------------------------------------------------------------------------------
def logout_view(request):
    logout(request)
    return render_to_response("session/login.html")
#------------------------------------------------------------------------------
@login_required
@csrf_protect
def corp(request):
    try:
        corp = Corp.objects.get(id=1)
        corp.description = re.subn(SHOWINFO_PATTERN, r"/members/\1", corp.description)[0]
    except ObjectDoesNotExist:
        corp = Corp(corporationName="No Corporation info")

    data = { 'corp' : corp }

    return render_to_response("corp.html", data, context_instance=RequestContext(request))
