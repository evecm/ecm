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

from ecm.view.auth.forms import PasswordChangeForm, PasswordResetForm, PasswordSetForm
from ecm.data.roles.models import RoleType

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

urlpatterns += patterns('ecm.view.assets.normal',
    ###########################################################################
    # ASSETS VIEWS
    (r'^assets$',                                   'root'),
    (r'^assets/data$',                              'systems_data'),
    (r'^assets/(\d+)/data$',                        'stations_data'),
    (r'^assets/(\d+)/(\d+)/data$',                  'hangars_data'),
    (r'^assets/(\d+)/(\d+)/(\d+)/data$',            'hangar_content_data'),
    (r'^assets/(\d+)/(\d+)/(\d+)/(\d+)/data$',      'can1_content_data'),
    (r'^assets/(\d+)/(\d+)/(\d+)/(\d+)/(\d+)/data$', 'can2_content_data'),
    (r'^assets/search$',                            'search_items'),
)

DATE = r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})"

urlpatterns += patterns('ecm.view.assets.diff',
    ###########################################################################
    # ASSET DIFF VIEWS
    (r'^assets/changes$',                           'last_date'),
    (r'^assets/changes/' + DATE + r'$',              'root'),
    (r'^assets/changes/' + DATE + r'/data$',         'systems_data'),
    (r'^assets/changes/' + DATE + r'/(\d+)/data$',   'stations_data'),
    (r'^assets/changes/' + DATE + r'/(\d+)/(\d+)/data$', 'hangars_data'),
    (r'^assets/changes/' + DATE + r'/(\d+)/(\d+)/(\d+)/data$', 'hangar_contents_data'),
    (r'^assets/changes/' + DATE + r'/search$',       'search_items'),
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
)

urlpatterns += patterns('ecm.view.api',
    ###########################################################################
    # JSON API VIEWS
    (r'^api/players$',               'players'),
    (r'^api/bindings/(\w+)/users$',  'user_bindings'),
    (r'^api/bindings/(\w+)/groups$', 'group_bindings'),
)


###############################################################################
#                                 ECM MENU                                    #
###############################################################################
role_types = []
for rt in RoleType.objects.all().order_by('id'):
    role_types.append({'item_title': rt.dispName, 'item_url': '/roles/%s' % rt.typeName})

ecm_menus = [
    {'menu_title': 'Home',      'menu_url': '/',            'menu_items': []},
    {'menu_title': 'Dashboard', 'menu_url': '/dashboard',   'menu_items': []},
    {'menu_title': 'Members',   'menu_url': '/members',     'menu_items': [
        {'item_title': 'History', 'item_url': '/members/history'},
        {'item_title': 'Access Changes', 'item_url': '/members/accesschanges'},
        {'item_title': 'Unassociated Members', 'item_url': '/members/unassociated'},
    ]},
    {'menu_title': 'Titles',    'menu_url': '/titles',      'menu_items': [
        {'item_title': 'Changes', 'item_url': '/titles/changes'},
    ]},
    {'menu_title': 'Roles',     'menu_url': '/roles',       'menu_items': role_types},
    {'menu_title': 'Accounting',    'menu_url': '/accounting',      'menu_items': [
        {'item_title': 'Wallets Journal', 'item_url': '/accounting/journal'},
        {'item_title': 'Tax Contributions', 'item_url': '/accounting/contributions'},
    ]},
    {'menu_title': 'Assets',    'menu_url': '/assets',      'menu_items': [
        {'item_title': 'Changes', 'item_url': '/assets/changes'},
    ]},
    {'menu_title': 'Players',   'menu_url': '/players',     'menu_items': []},
    {'menu_title': 'Scheduled Tasks',   'menu_url': '/tasks',     'menu_items': []},
]
