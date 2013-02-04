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

__date__ = "2010-01-24"
__author__ = "diabeteman"


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from ecm.apps.hr.models import Member,\
                               Role,\
                               RoleType,\
                               Title,\
                               RoleMembership,\
                               TitleMembership,\
                               MemberDiff,\
                               TitleComposition,\
                               TitleCompoDiff,\
                               TitleMemberDiff,\
                               RoleMemberDiff,\
                               Recruit

class MemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'nickname', 'owner', 'corpDate', 'lastLogin']
    search_fields = ['name', 'nickname', 'owner__username']

class RecruitInline(admin.StackedInline):
    model = Recruit
    fk_name = 'user'
    can_delete = False

class UserAdmin(UserAdmin):
    inlines = (RecruitInline, )

admin.site.register(Member, MemberAdmin)
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
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

