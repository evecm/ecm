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

from django.conf.urls.defaults import patterns
urlpatterns = patterns('ecm.plugins.industry.views',
    (r'^$',                                     'home'),
)
urlpatterns += patterns('ecm.plugins.industry.views.orders',
    (r'^orders/$',                              'orders'),
    (r'^orders/all/data/$',                     'orders_data'),
    (r'^orders/(\d+)/$',                        'details'),
    (r'^orders/(\d+)/(\w+)/$',                  'change_state'),
)
urlpatterns += patterns('ecm.plugins.industry.views.catalog.items',
    (r'^catalog/$',                             'items'),
    (r'^catalog/items/$',                       'items'),
    (r'^catalog/items/data/$',                  'items_data'),
    (r'^catalog/items/(\d+)/$',                 'details'),
    (r'^catalog/items/(\d+)/price/$',           'price'),
    (r'^catalog/items/(\d+)/updateprodcost/$',  'updateprodcost'),
    (r'^catalog/items/(\d+)/updatepubprice/$',  'updatepublicprice'),
    (r'^catalog/items/(\d+)/availability/$',    'availability'),
    (r'^catalog/items/(\d+)/addblueprint/$',    'blueprint_add'),
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
