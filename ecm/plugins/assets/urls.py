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

__date__ = "2011 10 14"
__author__ = "diabeteman"

from django.conf.urls import patterns

urlpatterns = patterns('ecm.plugins.assets.views.normal',
    ###########################################################################
    # ASSETS VIEWS
    (r'^$',                                             'root'),
    (r'^data/$',                                        'get_systems_data'),
    (r'^(\d+)/data/$',                                  'get_celestial_objects_data'),
    (r'^(\d+)/(\d+)/data/$',                            'get_stations_data'),
    (r'^(\d+)/(\d+)/(\d+)/data/$',                      'get_hangars_data'),
    (r'^(\d+)/(\d+)/(\d+)/(\d+)/data/$',                'get_hangar_content_data'),
    (r'^(\d+)/(\d+)/(\d+)/(\d+)/(\d+)/data/$',          'get_can1_content_data'),
    (r'^(\d+)/(\d+)/(\d+)/(\d+)/(\d+)/(\d+)/data/$',    'get_can2_content_data'),
    (r'^search/$',                                      'search_items'),
)

DATE = r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})"

urlpatterns += patterns('ecm.plugins.assets.views.diff',
    ###########################################################################
    # ASSET DIFF VIEWS
    (r'^changes/$',                                      'last_date'),
    (r'^changes/dates/$',                                'get_dates'),
    (r'^changes/' + DATE + r'/$',                        'root'),
    (r'^changes/' + DATE + r'/data/$',                   'get_systems_data'),
    (r'^changes/' + DATE + r'/(\d+)/data/$',             'get_stations_data'),
    (r'^changes/' + DATE + r'/(\d+)/(\d+)/data/$',       'get_hangars_data'),
    (r'^changes/' + DATE + r'/(\d+)/(\d+)/(\d+)/data/$', 'get_hangar_content_data'),
    (r'^changes/' + DATE + r'/search/$',                 'search_items'),
)