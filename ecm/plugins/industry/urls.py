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

__date__ = "2011 11 8"
__author__ = "diabeteman"

from django.conf.urls import patterns
urlpatterns = patterns('ecm.plugins.industry.views',
    (r'^$',                                     'home'),
    (r'^catalog/$',                             'catalog.home'),
)
urlpatterns += patterns('ecm.plugins.industry.views.jobs',
    (r'^jobs/$',                                'jobs_list'),
    (r'^jobs/data/$',                           'jobs_list_data'),
    (r'^jobs/(\d+)/(\w+)/$',                    'change_state'),
)
urlpatterns += patterns('ecm.plugins.industry.views.orders',
    (r'^orders/$',                              'orders'),
    (r'^orders/data/$',                         'orders_data'),
    (r'^orders/(\d+)/$',                        'details'),
    (r'^orders/(\d+)/comment/$',                'add_comment'),
    (r'^orders/(\d+)/(\w+)/$',                  'change_state'),
)
urlpatterns += patterns('ecm.plugins.industry.views.catalog.items',
    (r'^catalog/items/$',                       'items'),
    (r'^catalog/items/data/$',                  'items_data'),
    (r'^catalog/items/(\d+)/$',                 'details'),
    (r'^catalog/items/(\d+)/fixed_price/$',     'fixed_price'),
    (r'^catalog/items/(\d+)/production_cost/$', 'production_cost'),
    (r'^catalog/items/(\d+)/public_price/$',    'public_price'),
    (r'^catalog/items/(\d+)/availability/$',    'availability'),
    (r'^catalog/items/(\d+)/add_blueprint/$',   'add_blueprint'),
)
urlpatterns += patterns('ecm.plugins.industry.views.catalog.import_blueprints',
    (r'^catalog/blueprints/import/$',           'blueprints'),
    (r'^catalog/blueprints/import/data/$',      'blueprints_data'),
)
urlpatterns += patterns('ecm.plugins.industry.views.catalog.blueprints',
    (r'^catalog/blueprints/$',                  'blueprints'),
    (r'^catalog/blueprints/data/$',             'blueprints_data'),
    (r'^catalog/blueprints/(\d+)/$',            'details'),
    (r'^catalog/blueprints/(\d+)/materials/$',  'materials'),
    (r'^catalog/blueprints/(\d+)/time/$',       'manufacturing_time'),
    (r'^catalog/blueprints/(\d+)/delete/$',     'delete'),
    (r'^catalog/blueprints/(\w+)/$',            'info'),
)
urlpatterns += patterns('ecm.plugins.industry.views.catalog.supplies',
    (r'^catalog/supplies/$',                    'supplies'),
    (r'^catalog/supplies/data/$',               'supplies_data'),
    (r'^catalog/supplies/(\d+)/$',              'details'),
    (r'^catalog/supplies/(\d+)/data/$',         'details_data'),
    (r'^catalog/supplies/(\d+)/updateprice/$',  'update_price'),
    (r'^catalog/supplies/(\w+)/$',              'info'),
)
