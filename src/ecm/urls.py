# Copyright (c) 2010-2011 Robin Jarry
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

from django.conf.urls.defaults import patterns, include
from django.conf import settings
from django.contrib import admin

from ecm import plugins
from ecm.view.auth.forms import PasswordChangeForm, PasswordResetForm, PasswordSetForm

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
    (r'^account/login$',                'login',
                                            {'template_name' : 'auth/login.html'}),
    (r'^account/logout$',               'logout',
                                            {'next_page' : '/'}),
    (r'^account/passwordchange$',       'password_change',
                                            {'template_name' : 'auth/password_change.html',
                                            'password_change_form' : PasswordChangeForm}),
    (r'^account/passwordchange/done$',  'password_change_done',
                                            {'template_name' : 'auth/password_change_done.html'}),
    (r'^account/passwordreset$',        'password_reset',
                                            {'template_name' : 'auth/password_reset.html',
                                             'email_template_name' : 'auth/password_reset_email.txt',
                                             'password_reset_form' : PasswordResetForm,
                                             'post_reset_redirect' : '/account/passwordreset/sent'}),
    (r'^account/passwordreset/sent$',   'password_reset_done',
                                            {'template_name' : 'auth/password_reset_done.html'}),
    (r'^account/passwordreset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)$','password_reset_confirm',
                                            {'template_name' : 'auth/password_reset_confirm.html',
                                             'set_password_form' : PasswordSetForm}),
    (r'^account/passwordreset/complete$','password_reset_complete',
                                            {'template_name' : 'auth/password_reset_complete.html'}),

)

urlpatterns += patterns('ecm.view.auth',
    ###########################################################################
    # ECM AUTH + USER PROFILE VIEWS
    (r'^account$',                       'account.account'),
    (r'^account/addapi$',                'account.add_api'),
    (r'^account/deleteapi/(\d+)$',       'account.delete_api'),
    (r'^account/deletecharacter/(\d+)$', 'account.delete_character'),
    (r'^account/editapi/(\d+)$',         'account.edit_api'),
    (r'^account/binding/add/(\d+)$',     'account.add_binding'),
    (r'^account/binding/delete/(\d+)$',  'account.delete_binding'),

    (r'^account/create$',                'signup.create_account'),
    (r'^account/activate/(\w+)$',        'signup.activate_account'),

    (r'^players$',                       'players.player_list'),
    (r'^players/data$',                  'players.player_list_data'),
    (r'^players/(\d+)$',                 'players.player_details'),
    (r'^players/(\d+)/data$',            'players.player_details_data'),
)

urlpatterns += patterns('ecm.view',
    ###########################################################################
    # COMMON VIEWS
    (r'^$',                     'common.corp'),
    (r'^dashboard$',            'dashboard.dashboard'),
    (r'^cron$',                 'common.trigger_scheduler'),
    (r'^tasks$',                'common.task_list'),
    (r'^tasks/data$',           'common.task_list_data'),
    (r'^tasks/(\d+)/launch$',   'common.launch_task'),
)

urlpatterns += patterns('ecm.view.members',
    ###########################################################################
    # MEMBERS VIEWS
    (r'^members$',                          'list.all'),
    (r'^members/data$',                     'list.all_data'),
    (r'^members/history$',                  'history.history'),
    (r'^members/history/data$',             'history.history_data'),
    (r'^members/unassociated$',             'list.unassociated'),
    (r'^members/unassociated/data$',        'list.unassociated_data'),
    (r'^members/unassociated/clip$',        'list.unassociated_clip'),
    (r'^members/accesschanges$',            'access.access_changes'),
    (r'^members/accesschanges/data$',       'access.access_changes_data'),
    (r'^members/(\d+)$',                    'details.details'),
    (r'^members/(\d+)/accesschanges/data',  'details.access_changes_member_data'),
    (r'^members/(\d+)/updatenotes',         'details.update_member_notes'),
)

urlpatterns += patterns('ecm.view.titles',
    ###########################################################################
    # TITLES VIEWS
    (r'^titles$',                        'list.all'),
    (r'^titles/data$',                   'list.all_data'),
    (r'^titles/changes$',                'changes.changes'),
    (r'^titles/changes/data$',           'changes.changes_data'),
    (r'^titles/(\d+)$',                  'details.details'),
    (r'^titles/(\d+)/composition/data$', 'details.composition_data'),
    (r'^titles/(\d+)/compodiff/data$',   'details.compo_diff_data'),
    (r'^titles/(\d+)/members$',          'members.members'),
    (r'^titles/(\d+)/members/data$',     'members.members_data'),
)

urlpatterns += patterns('ecm.view.roles',
    ###########################################################################
    # ROLES VIEWS
    (r'^roles$',                         'list.root'),
    (r'^roles/update$',                  'list.update_access_level'),
    (r'^roles/([a-zA-Z_]+)$',            'list.role_type'),
    (r'^roles/([a-zA-Z_]+)/data$',       'list.role_type_data'),
    (r'^roles/([a-zA-Z_]+)/(\d+)$',      'details.role'),
    (r'^roles/([a-zA-Z_]+)/(\d+)/data$', 'details.role_data'),
)


urlpatterns += patterns('ecm.view.accounting',
    ###########################################################################
    # ACCOUNTING VIEWS
    (r'^accounting$',               'wallets.list'),
    (r'^accounting/wallets/data$',  'wallets.list_data'),
    (r'^accounting/journal$',       'journal.list'),
    (r'^accounting/journal/data$',  'journal.list_data'),
    (r'^accounting/contributions$', 'contrib.member_contrib'),
    (r'^accounting/contributions/members/data$', 'contrib.member_contrib_data'),
    (r'^accounting/contributions/systems/data$', 'contrib.system_contrib_data'),
    (r'^accounting/contributions/total/data$', 'contrib.total_contrib_data'),

)

urlpatterns += patterns('ecm.view.api',
    ###########################################################################
    # JSON API VIEWS
    (r'^api/players$',               'players'),
    (r'^api/bindings/(\w+)/users$',  'user_bindings'),
    (r'^api/bindings/(\w+)/groups$', 'group_bindings'),
)


PLUGINS_URLS = []
for app_prefix, urlconf in plugins.URLS:
    PLUGINS_URLS.append( (r'^' + app_prefix + '/', include(urlconf)) )

if PLUGINS_URLS:
    urlpatterns += patterns('',  *PLUGINS_URLS)

