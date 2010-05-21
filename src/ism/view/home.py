'''
This file is part of ICE Security Management

Created on 3 fev. 2010
@author: diabeteman
'''

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.template.context import RequestContext

from ism.data.roles.models import MemberDiff, RoleMemberDiff, TitleCompoDiff
from ism.core.utils import print_time_min

#------------------------------------------------------------------------------
@login_required
@csrf_protect
def home(request):
    data = {   'last_corped_members' : getLastCorpedMembers(),
             'last_expelled_members' : getLastExpelledMembers(),
                    'last_role_adds' : getLastRoleAdds(),
                'last_role_removals' : getLastRoleRemovals(),
              'last_title_role_adds' : getLastTitleRoleAdds(),
          'last_title_role_removals' : getLastTitleRoleRemovals()  }
    
    return render_to_response("home.html", data, context_instance=RequestContext(request))


#------------------------------------------------------------------------------
def getLastCorpedMembers(count=10):
    members = MemberDiff.objects.filter(new=True).order_by('-id')[:count]
    for m in members:
        m.date = print_time_min(m.date)
    return members

#------------------------------------------------------------------------------
def getLastExpelledMembers(count=10):
    members = MemberDiff.objects.filter(new=False).order_by('-id')[:count]
    for m in members:
        m.date = print_time_min(m.date)
    return members

#------------------------------------------------------------------------------
def getLastRoleAdds(count=10):
    roles = RoleMemberDiff.objects.filter(new=True).order_by('-id')[:count]
    for r in roles:
        r.date = print_time_min(r.date)
    return roles

#------------------------------------------------------------------------------
def getLastRoleRemovals(count=10):
    roles = RoleMemberDiff.objects.filter(new=False).order_by('-id')[:count]
    for r in roles:
        r.date = print_time_min(r.date)
    return roles

#------------------------------------------------------------------------------
def getLastTitleRoleAdds(count=10):
    titles = TitleCompoDiff.objects.filter(new=True).order_by('-id')[:count]
    for t in titles:
        t.date = print_time_min(t.date)
    return titles

#------------------------------------------------------------------------------
def getLastTitleRoleRemovals(count=10):
    titles = TitleCompoDiff.objects.filter(new=False).order_by('-id')[:count]
    for t in titles:
        t.date = print_time_min(t.date)
    return titles
#------------------------------------------------------------------------------