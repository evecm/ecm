# Copyright (c) 2010-2012 Robin Jarry, Ajurna
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

__date__ = "2012 03 17"
__author__ = "diabeteman"

from django.shortcuts import render_to_response
from django.template.context import RequestContext as Ctx

def home(request):
    return render_to_response('ecm/industry/catalog/catalog_home.html', {}, Ctx(request))