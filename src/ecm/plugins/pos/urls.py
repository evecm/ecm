# Copyright (c) 2010-2011 Jerome Vacher
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

__date__ = "2011 10 30"
__author__ = "JerryKhan"

from django.conf.urls.defaults import patterns

urlpatterns = patterns('ecm.plugins.pos.views',
    ###########################################################################
    # POS VIEWS
    (r'^$',                                     'pos_list.all'),          # To access the list definition 
    (r'^list$',                                 'pos_list.all'),          # To access the list definition
    (r'^data$',                                 'pos_list.all_data'),     # for table jquery content getter
    (r'^test',                                  'pos_list.test'),         # for table jquery content getter
    (r'^(\d+)$',                                'pos_details.onePos'),    # TO BE DEFINED
    (r'^(\d+)/data$',                           'pos_details.fuel_data'), # NOT SURE IT IS NECESSARY NOW
)

