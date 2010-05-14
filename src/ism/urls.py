'''
This file is part of ICE Security Management

Created on 24 jan. 2010

@author: diabeteman
'''

from ism.view import home
from ism import settings

from django.conf.urls.defaults import patterns, include, url
from django.views import static

from django.contrib import admin
from django.contrib import databrowse
admin.autodiscover()


urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # ISM views
    (r'^$', home.home),
    (r'^media/(?P<path>.*)$', static.serve, {'document_root' : settings.MEDIA_ROOT, 'show_indexes' : True}),
)