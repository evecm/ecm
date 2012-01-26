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
    ###########################################################################
    # INDUSTRY VIEWS
    (r'^search/data$',                          'search_item'),
    (r'^search/itemid$',                        'get_item_id'),

    (r'^orders/$',                              'orders.orders'),
    (r'^orders/all/data/$',                     'orders.orders_data'),
    (r'^orders/(\d+)/$',                        'orders.details'),
    (r'^orders/(\d+)/(\w+)/$',                  'orders.change_state'),

    (r'^catalog/items/$',                       'catalog.items.items'),
    (r'^catalog/items/data/$',                  'catalog.items.items_data'),
    (r'^catalog/items/(\d+)/$',                 'catalog.items.details'),
    (r'^catalog/items/(\d+)/price/$',           'catalog.items.price'),
    (r'^catalog/items/(\d+)/availability/$',    'catalog.items.availability'),
    (r'^catalog/items/(\d+)/addblueprint/$',    'catalog.items.blueprint_add'),

    (r'^catalog/blueprints/$',                  'catalog.blueprints.blueprints'),
    (r'^catalog/blueprints/data/$',             'catalog.blueprints.blueprints_data'),
    (r'^catalog/blueprints/(\d+)/$',            'catalog.blueprints.details'),
    (r'^catalog/blueprints/(\d+)/materials/$',  'catalog.blueprints.materials'),
    (r'^catalog/blueprints/(\d+)/time/$',       'catalog.blueprints.manufacturing_time'),
    (r'^catalog/blueprints/(\d+)/delete/$',     'catalog.blueprints.delete'),
    (r'^catalog/blueprints/(\w+)/$',            'catalog.blueprints.info'),

    (r'^catalog/supplies/$',                    'catalog.supplies.supplies'),
    (r'^catalog/supplies/data/$',               'catalog.supplies.supplies_data'),
    (r'^catalog/supplies/(\d+)/$',              'catalog.supplies.details'),
    (r'^catalog/supplies/(\d+)/data/$',         'catalog.supplies.details_data'),
    (r'^catalog/supplies/(\d+)/updateprice/$',  'catalog.supplies.update_price'),
    (r'^catalog/supplies/(\w+)/$',              'catalog.supplies.info'),
)

