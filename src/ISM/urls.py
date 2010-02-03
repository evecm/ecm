'''
This file is part of ICE Security Management

Created on 24 jan. 2010

@author: diabeteman
'''

import roles.views
import ISM.settings
import ISM.views
from django.conf.urls.defaults import patterns, include
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib import databrowse
import django.views.static
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^$', ISM.views.home),
    (r'^stuff/(?P<path>.*)$', django.views.static.serve, {'document_root': ISM.settings.MEDIA_ROOT}),

    (r'^titles/$', roles.views.titles),
    (r'^titles/(?P<title_id>\d+)/$', roles.views.titleDetails),
    (r'^browse/(.*)', databrowse.site.root),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^browse/(.*)', databrowse.site.root),
)
