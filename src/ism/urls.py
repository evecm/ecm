'''
This file is part of ICE Security Management

Created on 24 jan. 2010

@author: diabeteman
'''

from ism.view import home, members, assets, titles
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
    (r'^admin', include(admin.site.urls)),
    # ISM views
    (r'^%s$' % settings.LOGIN_URL[1:], 'django.contrib.auth.views.login', {'template_name' : 'session/login.html'}),
    (r'^%s$' % settings.LOGOUT_URL[1:], 'django.contrib.auth.views.logout', {'next_page' : '/'}),
    (r'^user/change_password$', 'django.contrib.auth.views.password_change', {'template_name' : 'session/password_change.html', 'post_change_redirect' : '/'}), 
    
    
    (r'^$', home.home),
    (r'^members$',         members.all),
    (r'^members/history$', members.history),
    (r'^members/(\d+)$',   members.details),
    
    (r'^titles$', titles.titles),
    
    
    (r'^assets$',                         assets.stations),
    (r'^assets/(\d+)$',                   assets.hangars),
    (r'^assets/(\d+)/(\d+)$',             assets.hangar_contents),
    (r'^assets/(\d+)/(\d+)/(\d+)$',       assets.can1_contents),
    (r'^assets/(\d+)/(\d+)/(\d+)/(\d+)$', assets.can2_contents),
    (r'^assets/search$',                  assets.search_items),

    (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], static.serve, {'document_root' : settings.MEDIA_ROOT}),
)
