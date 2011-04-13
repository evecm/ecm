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
from ecm.core.utils import get_access_color
from django.shortcuts import render_to_response
from django.template.context import RequestContext

__date__ = "2011 4 13"
__author__ = "diabeteman"


from ecm.data.common.models import ColorThreshold
from ecm.data.roles.models import Member

def access_lvl_repartition(request):
    colors = {}
    thresholds = ColorThreshold.objects.all()
    for th in thresholds:
        colors[th.color] = th
        th.members = 0
    
    for member in Member.objects.filter(corped=True):
        colors[get_access_color(member.accessLvl, thresholds)].members += 1
    
    return render_to_response('members/dashboard.html', {'colors':colors}, RequestContext(request))
    