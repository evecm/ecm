'''
This file is part of ESM

Created on 2 march 2011
@author: diabeteman
'''

import json

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from django.utils.text import truncate_words
from django.http import HttpResponse

from ism.data.roles.models import TitleComposition, Title, TitleCompoDiff, TitleMembership, Member,\
    Role, RoleType
from ism.data.common.models import UpdateDate, ColorThreshold
from ism.core import utils
from ism.core.utils import print_time_min, print_date, getAccessColor
from ism import settings

ROLE_TYPES = {}
for t in RoleType.objects.all(): ROLE_TYPES[t.typeName] = t.id

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def all(request):
    thresholds = ColorThreshold.objects.all().order_by("threshold").values("threshold", "color")

    data = { 
        'colorThresholds' : json.dumps(thresholds)
    }
    return render_to_response("roles.html", data, context_instance=RequestContext(request))



#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def general(request):
    thresholds = ColorThreshold.objects.all().order_by("threshold").values("threshold", "color")
    roles = Role.objects.filter(roleType=ROLE_TYPES["roles"])
    




    data = { 
        'colorThresholds' : json.dumps(thresholds)
    }
    return 
