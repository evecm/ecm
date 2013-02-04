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

__date__ = "2011 9 6"
__author__ = "diabeteman"

from ecm.apps.hr.models.member import Member, MemberDiff, Recruit, Skill #@UnusedImport
from ecm.apps.hr.models.roles import RoleType, Role, RoleMembership, RoleMemberDiff #@UnusedImport
from ecm.apps.hr.models.titles import (Title, #@UnusedImport
                                       TitleComposition,  #@UnusedImport
                                       TitleMembership,  #@UnusedImport
                                       TitleCompoDiff,  #@UnusedImport
                                       TitleMemberDiff) #@UnusedImport

# How to split models in separate python modules
# http://www.acooke.org/cute/UsingaDire0.html

__all__ = (
    'Member',
    'MemberDiff',
    'Skill',
    
    'RoleType',
    'Role',
    'RoleMembership',
    'RoleMemberDiff',
    
    'Title',
    'TitleComposition',
    'TitleMembership',
    'TitleCompoDiff',
    'TitleMemberDiff',

    'Recruit',
)
