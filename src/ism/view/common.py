'''
This file is part of ICE Security Management

Created on 16 mai 2010
@author: diabeteman
'''


from django.shortcuts import render_to_response

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return render_to_response("login.html")
