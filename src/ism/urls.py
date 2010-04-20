'''
This file is part of ICE Security Management

Created on 24 jan. 2010

@author: diabeteman
'''

from ism.roles.views import titles, titleDetails
from ism.views import home
from ism.settings import MEDIA_ROOT
from django.conf.urls.defaults import patterns, include
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib import databrowse
import django.views.static
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^$', home),
    (r'^stuff/(?P<path>.*)$', django.views.static.serve, {'document_root': MEDIA_ROOT}),

    (r'^titles/$', titles),
    (r'^titles/(?P<title_id>\d+)/$', titleDetails),
    (r'^browse/(.*)', databrowse.site.root),
    
    #Edited by Naskaya
    (r'^services/$', 'ISM.view.entrypoint.service'),
    (r'^ISM/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.STATIC}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^browse/(.*)', databrowse.site.root),
)
