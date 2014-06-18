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

urlpatterns = patterns('ecm.plugins.shop.views',
    (r'^$',                     'home'),

    (r'^utils/parseeft/$',      'utils.parse_eft'),
    (r'^utils/search/$',        'utils.search_item'),
    (r'^utils/itemid/$',        'utils.get_item_id'),

    (r'^orders/$',              'orders.myorders'),
    (r'^orders/data/$',         'orders.myorders_data'),
    (r'^orders/create/$',       'orders.create'),
    (r'^orders/(\d+)/$',        'orders.details'),
    (r'^orders/(\d+)/comment/$','orders.add_comment'),
    (r'^orders/(\d+)/(\w+)/$',  'orders.change_state'),
)

