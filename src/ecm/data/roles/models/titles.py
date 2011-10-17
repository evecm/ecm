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

__date__ = "2011 9 6"
__author__ = "diabeteman"


from datetime import datetime

from django.db import models

from ecm.lib import bigintpatch
from ecm.data.roles.models.member import Member
from ecm.data.roles.models.roles import Role


#------------------------------------------------------------------------------
class Title(models.Model):
    """
    Corporation Title. Titles are an aggregation of multiple Roles
    """

    class Meta:
        app_label = 'roles'
        ordering = ['titleID']

    titleID = models.BigIntegerField(primary_key=True)
    titleName = models.CharField(max_length=256)
    tiedToBase = models.BigIntegerField(default=0)
    accessLvl = models.BigIntegerField(default=0)

    members = models.ManyToManyField(Member, through='TitleMembership', related_name="titles")
    roles = models.ManyToManyField(Role, through='TitleComposition', related_name="titles")

    def get_access_lvl(self):
        lvl = 0
        for r in self.roles.all() :
            lvl += r.get_access_lvl()
        return lvl

    @property
    def url(self):
        return '/titles/%d/' % self.titleID

    @property
    def permalink(self):
        return '<a href="%s" class="title">%s</a>' % (self.url, self.titleName)

    def __eq__(self, other):
        return self.titleID == other.titleID

    def __hash__(self):
        return self.titleID

    def __unicode__(self):
        return unicode(self.titleName)




#------------------------------------------------------------------------------
class TitleMembership(models.Model):
    """
    Represents the assignment of one Title to a Member.
    """

    class Meta:
        app_label = 'roles'
        ordering = ['member']

    member = models.ForeignKey(Member)
    title = models.ForeignKey(Title)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return self.member_id * 100000 + self.title_id

    def __unicode__(self):
        try:
            return unicode(self.member) + u' is ' + unicode(self.title)
        except:
            return u'member_id:%d is %s' % (self.member_id, str(self.title))

#------------------------------------------------------------------------------
class TitleComposition(models.Model):
    """
    Represents the association of one Role to a Title.
    """

    class Meta:
        app_label = 'roles'
        ordering = ['title']

    title = models.ForeignKey(Title)
    role = models.ForeignKey(Role)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return self.title_id * 1000 + self.role_id

    def __unicode__(self):
        return unicode(self.title) + u' has ' + unicode(self.role)


#------------------------------------------------------------------------------
class TitleCompoDiff(models.Model):
    """
    Represents the unitary modification of a Title (added or removed Role)
    """

    class Meta:
        app_label = 'roles'
        ordering = ['date']

    id = bigintpatch.BigAutoField(primary_key=True)
    title = models.ForeignKey(Title)
    role = models.ForeignKey(Role)
    # true if role is new in title, false if role was removed
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.DateTimeField(db_index=True, default=datetime.now())

    def __unicode__(self):
        if self.new: return unicode(self.title) + u' gets ' + unicode(self.role)
        else       : return unicode(self.title) + u' looses ' + unicode(self.role)



#------------------------------------------------------------------------------
class TitleMemberDiff(models.Model):
    """
    Represents the change in the assignment of a Title to a Member
    """

    class Meta:
        app_label = 'roles'
        ordering = ['date']

    id = bigintpatch.BigAutoField(primary_key=True)
    member = models.ForeignKey(Member)
    title = models.ForeignKey(Title)
    # true if title is new for member, false if title was removed
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.DateTimeField(db_index=True, default=datetime.now())

    @property
    def access_permalink(self):
        return self.title.permalink

    @property
    def member_permalink(self):
        try:
            return self.member.permalink
        except:
            # this could fail if the RoleMemberDiff has been recorded from
            # /corp/MemberSecurity.xml.aspx but that the member has not been
            # parsed from /corp/MemberTracking.xml.aspx yet
            return '<a href="/members/%d/" class="member">???</a>' % self.member_id

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

    def __unicode__(self):
        try:
            membername = self.member.name
        except:
            membername = str(self.member_id)
        if self.new: return '%s got %s' % (membername, self.title.titleName)
        else       : return '%s lost %s' % (membername, self.title.titleName)

