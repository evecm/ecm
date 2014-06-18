# Copyright (c) 2010-2012 Robin Jarry
#
# This file is part of EVE Corporation Management.
#
# EVE Corporation Management is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# EVE Corporation Management is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

__date__ = "2010-01-24"
__author__ = "diabeteman"

from django.conf.urls import patterns, include
from django.contrib import admin
from django.http import HttpResponse
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from ecm.views.account.forms import PasswordChangeForm, PasswordResetForm, PasswordSetForm

admin.autodiscover()

def robots(request):
    return HttpResponse("User-agent: *\nDisallow: /", mimetype="text/plain")

urlpatterns = patterns('',
    ###########################################################################
    # MISC VIEWS
    (r'^robots\.txt$',                              robots),
    (r'^admin/',                                    include(admin.site.urls)),
    (r'^captcha/',                                  include('captcha.urls')),
)

urlpatterns += staticfiles_urlpatterns()

urlpatterns += patterns('django.contrib.auth.views',
    ###########################################################################
    # DJANGO BUILT-IN AUTH VIEWS
    (r'^account/login/$',                'login',
                                            {'template_name' : 'ecm/auth/login.html'}),
    (r'^account/logout/$',               'logout',
                                            {'next_page' : '/'}),
    (r'^account/passwordchange/$',       'password_change',
                                            {'template_name' : 'ecm/auth/password_change.html',
                                            'password_change_form' : PasswordChangeForm}),
    (r'^account/passwordchange/done/$',  'password_change_done',
                                            {'template_name' : 'ecm/auth/password_change_done.html'}),
    (r'^account/passwordreset/$',        'password_reset',
                                            {'template_name' : 'ecm/auth/password_reset.html',
                                             'email_template_name' : 'ecm/auth/password_reset_email.txt',
                                             'password_reset_form' : PasswordResetForm,
                                             'post_reset_redirect' : '/account/passwordreset/sent/'}),
    (r'^account/passwordreset/sent/$',   'password_reset_done',
                                            {'template_name' : 'ecm/auth/password_reset_done.html'}),
    (r'^account/passwordreset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$','password_reset_confirm',
                                            {'template_name' : 'ecm/auth/password_reset_confirm.html',
                                             'set_password_form' : PasswordSetForm}),
    (r'^account/passwordreset/complete/$','password_reset_complete',
                                            {'template_name' : 'ecm/auth/password_reset_complete.html'}),
)

urlpatterns += patterns('ecm.views.account',
    ###########################################################################
    # ECM AUTH + USER PROFILE VIEWS
    (r'^account/$',                       'home.account'),
    (r'^account/addapi/$',                'home.add_api'),
    (r'^account/deleteapi/(\d+)/$',       'home.delete_api'),
    (r'^account/deletecharacter/(\d+)/$', 'home.delete_character'),
    (r'^account/editapi/(\d+)/$',         'home.edit_api'),
    (r'^account/binding/add/(\d+)/$',     'home.add_binding'),
    (r'^account/binding/delete/(\d+)/$',  'home.delete_binding'),

    (r'^account/create/$',                'signup.create_account'),
    (r'^account/activate/(\w+)/$',        'signup.activate_account'),

)

urlpatterns += patterns('ecm.views',
    ###########################################################################
    # COMMON VIEWS
    (r'^$',                     'common.home'),
    (r'^editmotd/$',            'common.edit_motd'),
    (r'^editapi/$',             'common.edit_apikey'),
)

urlpatterns += patterns('ecm.views.api',
    ###########################################################################
    # JSON API VIEWS
    (r'^api/players/$',               'players'),
    (r'^api/bindings/(\w+)/users/$',  'user_bindings'),
    (r'^api/bindings/(\w+)/groups/$', 'group_bindings'),
)

urlpatterns += patterns('ecm.views.ajax',
    ###########################################################################
    # AJAX QUERY VIEWS
    (r'^ajax/celestials/$',           'celestial.list'),
    (r'^ajax/solarsystems/$',         'solarsystem.list'),
    (r'^ajax/moons/$',                'moons.list'),
)


import ecm.apps
CORE_APPS_URLS = []
for app in ecm.apps.LIST:
    if app.urlconf is not None:
        CORE_APPS_URLS.append( (r'^' + app.app_prefix + '/', include(app.urlconf)) )
if CORE_APPS_URLS:
    urlpatterns += patterns('',  *CORE_APPS_URLS)


import ecm.plugins
PLUGINS_URLS = []
for plugin in ecm.plugins.LIST:
    PLUGINS_URLS.append( (r'^' + plugin.app_prefix + '/', include(plugin.urlconf)) )
if PLUGINS_URLS:
    urlpatterns += patterns('',  *PLUGINS_URLS)
    
################################################
#custom handlers for http return codes
handler500='ecm.views.custom_handlers.server_error'


