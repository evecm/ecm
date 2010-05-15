'''
This file is part of ICE Security Management

Created on 3 fev. 2010
@author: diabeteman
'''

from django.shortcuts import render_to_response
from ism.settings import MEDIA_URL

from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return render_to_response("home.html", {'MEDIA_URL' : MEDIA_URL,
                                            'PAGE_TITLE' : 'Home'})
