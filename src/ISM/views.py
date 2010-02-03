'''
This file is part of ICE Security Management

Created on 3 fev. 2010
@author: diabeteman
'''

from ISM.roles.models import Title
from django.shortcuts import render_to_response


def home(request):
    return render_to_response("home.html", {'title' : 'Home'})
