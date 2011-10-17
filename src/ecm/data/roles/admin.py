# Copyright (c) 2010-2011 Robin Jarry
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

__date__ = "2010-01-24"
__author__ = "diabeteman"


from django.contrib import admin

from ecm.data.roles.models import Role, Title, Member, RoleType, RoleMembership, MemberDiff,\
    TitleCompoDiff, TitleMemberDiff, RoleMemberDiff, TitleMembership, TitleComposition

admin.site.register(Member)
admin.site.register(Role)
admin.site.register(RoleType)
admin.site.register(Title)
admin.site.register(RoleMembership)
admin.site.register(TitleMembership)
admin.site.register(MemberDiff)
admin.site.register(TitleComposition)
admin.site.register(TitleCompoDiff)
admin.site.register(TitleMemberDiff)
admin.site.register(RoleMemberDiff)

