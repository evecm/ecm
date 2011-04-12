# The MIT License - EVE Corporation Management
# 
# Copyright (c) 2010 Robin Jarry
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__date__ = "2010-01-24"
__author__ = "diabeteman"

from django.conf.urls.defaults import patterns, include
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    ###########################################################################
    # MISC VIEWS
    (r'^admin/',                                    include(admin.site.urls)),
    (r'^captcha/',                                  include('captcha.urls')),
    # static file serving for the development server
    (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],  'django.views.static.serve', 
                                                    {'document_root' : settings.MEDIA_ROOT}),
)

urlpatterns += patterns('django.contrib.auth.views',
    ###########################################################################
    # DJANGO BUILT-IN AUTH VIEWS
    (r'^account/login$',                            'login', {'template_name' : 'auth/login.html'}),
    (r'^account/logout$',                           'logout', {'next_page' : '/'}),
    (r'^account/change_password$',                  'password_change', 
                                                    {'template_name' : 'auth/password_change.html', 
                                                     'post_change_redirect' : '/'}),
)
 
urlpatterns += patterns('ecm.view.auth',
    ###########################################################################
    # ECM AUTH + USER PROFILE VIEWS
    (r'^account$',                                  'user_profile'),
    (r'^account/create$',                           'signup.create_account'),
    (r'^account/activate/(\w+)$',                   'signup.activate_account'),
)

urlpatterns += patterns('ecm.view',
    ###########################################################################
    # COMMON VIEWS
    (r'^$',                                         'home.home'),
    (r'^corp$',                                     'common.corp'),
    (r'^cron$',                                     'common.trigger_scheduler'),
    (r'^tasks$',                                    'common.task_list'),
    (r'^tasks/launch/([^/]+)$',                     'common.launch_task'),
)

urlpatterns += patterns('ecm.view.members',
    ###########################################################################
    # MEMBERS VIEWS
    (r'^members$',                                  'list.all'),
    (r'^members/data$',                             'list.all_data'),
    (r'^members/history$',                          'history.history'),
    (r'^members/history/data$',                     'history.history_data'),
    (r'^members/access_changes$',                   'access.access_changes'),
    (r'^members/access_changes/data$',              'access.access_changes_data'),
    (r'^members/(\d+)$',                            'details.details'),
    (r'^members/(\d+)/access_changes_data',         'details.access_changes_member_data'),
)

urlpatterns += patterns('ecm.view.titles',
    ###########################################################################
    # TITLES VIEWS
    (r'^titles$',                                   'list.all'),
    (r'^titles/data$',                              'list.all_data'),
    (r'^titles/changes$',                           'changes.changes'),
    (r'^titles/changes/data$',                      'changes.changes_data'),
    (r'^titles/(\d+)$',                             'details.details'),
    (r'^titles/(\d+)/composition_data$',            'details.composition_data'),
    (r'^titles/(\d+)/compo_diff_data$',             'details.compo_diff_data'),
    (r'^titles/(\d+)/members$',                     'members.members'),
    (r'^titles/(\d+)/members/data$',                'members.members_data'),
)

urlpatterns += patterns('ecm.view.roles',
    ###########################################################################
    # ROLES VIEWS
    (r'^roles$',                                    'list.root'),
    (r'^roles/update$',                             'list.update_access_level'),
    (r'^roles/([a-zA-Z_]+)$',                       'list.role_type'),
    (r'^roles/([a-zA-Z_]+)/data$',                  'list.role_type_data'),
    (r'^roles/([a-zA-Z_]+)/(\d+)$',                 'details.role'),
    (r'^roles/([a-zA-Z_]+)/(\d+)/data$',            'details.role_data'),
)

urlpatterns += patterns('ecm.view.assets.normal',
    ###########################################################################
    # ASSETS VIEWS
    (r'^assets$',                                   'stations'),
    (r'^assets/(\d+)$',                             'hangars'),
    (r'^assets/(\d+)/(\d+)$',                       'hangar_contents'),
    (r'^assets/(\d+)/(\d+)/(\d+)$',                 'can1_contents'),
    (r'^assets/(\d+)/(\d+)/(\d+)/(\d+)$',           'can2_contents'),
    (r'^assets/search$',                            'search_items'),
)

DATE = r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})"

urlpatterns += patterns('ecm.view.assets.diff',
    ###########################################################################
    # ASSET DIFF VIEWS
    (r'^assets/changes$',                           'last_stations'),
    (r'^assets/changes/' + DATE + '$',              'stations'),
    (r'^assets/changes/' + DATE + '/(\d+)$',        'hangars'),
    (r'^assets/changes/' + DATE + '/(\d+)/(\d+)$',  'hangar_contents'),
    (r'^assets/changes/' + DATE + '/search$',       'search_items'),
)
