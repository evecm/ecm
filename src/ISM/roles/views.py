'''
This file is part of ICE Security Management

Created on 01 fev. 2010
@author: diabeteman
'''

from ISM.roles.models import Title, Role
from django.shortcuts import render_to_response



def titles(request):
    return render_to_response("titles.html", {'corp_titles' : Title.objects.all(),
                                              'roles'       : Role.objects.all(), 
                                              'title'       : 'Titles'})

def titleDetails(request, title_id):
    return render_to_response("base.html", {'page_title' : title_id,'title_id' : title_id})