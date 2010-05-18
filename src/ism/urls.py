'''
This file is part of ICE Security Management

Created on 24 jan. 2010

@author: diabeteman
'''

from ism.view import home, members
from ism import settings

from django.conf.urls.defaults import patterns, include
from django.views import static
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    # ISM views
    (r'^%s$' % settings.LOGIN_URL[1:], 'django.contrib.auth.views.login', {'template_name' : 'login.html'}),
    (r'^%s$' % settings.LOGOUT_URL[1:], 'django.contrib.auth.views.logout', {'next_page' : '/'}),
    
    
    
    (r'^$', home.home),
    (r'^members/list/$', members.list),
    
    
    
   # (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], static.serve, {'document_root' : settings.MEDIA_ROOT}),
)
