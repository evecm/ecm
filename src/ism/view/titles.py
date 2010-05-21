'''
This file is part of ICE Security Management

Created on 14 may 2010
@author: diabeteman
'''

from django.shortcuts import render_to_response
from ism.settings import MEDIA_URL

from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf

@login_required
@csrf_protect
def titles(request):
    return render_to_response("titles.html", {'MEDIA_URL' : MEDIA_URL,
                                              'PAGE_TITLE' : 'Home'})