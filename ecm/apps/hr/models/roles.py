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

from django.db import models

from ecm.lib import bigintpatch
from ecm.apps.corp.models import Hangar, Wallet, Corporation
from ecm.apps.hr.models.member import Member

#------------------------------------------------------------------------------
class RoleType(models.Model):
    """
    Category of Role
    """

    class Meta:
        app_label = 'hr'
        ordering = ['dispName']

    typeName = models.CharField(max_length=64, unique=True)
    dispName = models.CharField(max_length=64)

    @property
    def url(self):
        return '/hr/roles/?role_type=%d' % self.id

    @property
    def permalink(self):
        return '<a href="%s" class="role_type">%s</a>' % (self.url, self.dispName)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

    def __unicode__(self):
        if self.dispName:
            return unicode(self.dispName)
        else:
            return unicode(self.typeName)

#------------------------------------------------------------------------------
class Role(models.Model):
    """
    A Role gives a Member access to a specific resource of the Corporation.
    Such as the ability to view the content of a certain hangar division,
    to take money from a specific wallet division or the ability to operate
    starbase structures on behalf of the corporation.

    The potential risk of assigning a role to a member is represented by its accessLvl
    The accessLvl is to be set by the administrators according to the corporation's policies

    When a Role is related to hangar or wallet divisions, the accessLvl of the Role is
    that of the Hangar or Wallet division (not sure about my grammar here...)
    """

    class Meta:
        app_label = 'hr'
        ordering = ['id']

    roleType = models.ForeignKey(RoleType, db_index=True, related_name="roles")
    roleID = models.BigIntegerField()
    roleName = models.CharField(max_length=64)
    dispName = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    hangar = models.ForeignKey(Hangar, null=True, blank=True)
    wallet = models.ForeignKey(Wallet, null=True, blank=True)
    accessLvl = models.BigIntegerField(default=0)

    members = models.ManyToManyField(Member, through='RoleMembership', related_name="roles")

    def get_access_lvl(self):
        """
        Returns the accessLvl of the Role.
        If the Role is related to a Hangar or Wallet division,
        returns the accessLvl of this division.
        """
        my_corp = Corporation.objects.mine()
        if self.hangar_id:
            return self.hangar.get_access_lvl(my_corp)
        elif self.wallet_id:
            return self.wallet.get_access_lvl(my_corp)
        else:
            return self.accessLvl

    def members_through_titles(self, with_direct_roles=False):
        """
        Returns all Members that have this role assigned through Titles
        If with_direct_roles=True, also returns the Members who have this Role assigned directly
        """
        if with_direct_roles:
            members = self.members.all()
        else:
            members = Member.objects.none()
        for title in self.titles.all():
            members |= title.members.all()
        return members.distinct()

    def get_disp_name(self):
        my_corp = Corporation.objects.mine()
        name = self.dispName
        if self.hangar_id:
            name = name % self.hangar.get_name(my_corp)
        elif self.wallet_id:
            name = name % self.wallet.get_name(my_corp)
        return name

    @property
    def name(self):
        return self.get_disp_name()

    @property
    def url(self):
        return '/hr/roles/%d/' % self.id

    @property
    def permalink(self):
        try:
            return '<a href="%s" class="role">%s</a>' % (self.url, self.get_disp_name())
        except:
            return '<b>%s</b>' % self.get_disp_name()

    def __eq__(self, other):
        if other:
            return self.id == other.id
        else:
            return False

    def __hash__(self):
        return self.id

    def __unicode__(self):
        my_corp = Corporation.objects.mine()
        name = self.dispName
        if self.hangar_id:
            name = name % self.hangar.get_name(my_corp)
        elif self.wallet_id:
            name = name % self.wallet.get_name(my_corp)
        return "%s - %s" % (name, unicode(self.roleType))


#------------------------------------------------------------------------------
class RoleMembership(models.Model):
    """
    Represents the assignment of one Role to a Member.
    """

    class Meta:
        app_label = 'hr'
        ordering = ['member']

    member = models.ForeignKey(Member)
    role = models.ForeignKey(Role)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return self.member_id * 1000 + self.role_id

    def __unicode__(self):
        try:
            return u'%s has %s (%s)' % (unicode(self.member),
                                        unicode(self.role),
                                        unicode(self.role.roleType))
        except:
            return u'member_id:%d has %s (%s)' % (self.member_id,
                                                  unicode(self.role),
                                                  unicode(self.role.roleType))

#------------------------------------------------------------------------------
class RoleMemberDiff(models.Model):
    """
    Represents the change in the assignment of a Role to a Member
    """

    class Meta:
        app_label = 'hr'
        ordering = ['date']

    id = bigintpatch.BigAutoField(primary_key=True) #@ReservedAssignment
    member = models.ForeignKey(Member)
    role = models.ForeignKey(Role)
    # true if role is new for member, false if role was removed
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.DateTimeField(db_index=True, auto_now_add=True)

    DATE_FIELD = 'date' # used for garbage collection

    @property
    def access_permalink(self):
        return self.role.permalink

    @property
    def member_permalink(self):
        try:
            return self.member.permalink
        except:
            # this could fail if the RoleMemberDiff has been recorded from
            # /corp/MemberSecurity.xml.aspx but that the member has not been
            # parsed from /corp/MemberTracking.xml.aspx yet
            return '<a href="/hr/members/%d/" class="member">???</a>' % self.member_id

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

    def __unicode__(self):
        try:
            membername = self.member.name
        except:
            membername = unicode(self.member_id)
        if self.new: return u'%s got %s' % (membername, self.role.name)
        else       : return u'%s lost %s' % (membername, self.role.name)

