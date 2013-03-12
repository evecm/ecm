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

from ecm.apps.corp.models import Corporation
from ecm.apps.hr.models.member import Member
from ecm.apps.hr.models.roles import Role
from ecm.apps.hr import NAME as app_prefix

#------------------------------------------------------------------------------
class Title(models.Model):
    """
    Corporation Title. Titles are an aggregation of multiple Roles
    """

    class Meta:
        app_label = 'hr'
        ordering = ['titleID']
    
    corp = models.ForeignKey(Corporation, related_name='titles')
    titleID = models.BigIntegerField()
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
        return '/%s/titles/%d/' % (app_prefix, self.id)

    @property
    def permalink(self):
        return '<a href="%s" class="title">%s</a>' % (self.url, self.titleName)

    def __eq__(self, other):
        if other:
            return self.titleID == other.titleID
        else:
            return False 

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
        app_label = 'hr'
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
            return u'member_id:%d is %s' % (self.member_id, unicode(self.title))

#------------------------------------------------------------------------------
class TitleComposition(models.Model):
    """
    Represents the association of one Role to a Title.
    """

    class Meta:
        app_label = 'hr'
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
        app_label = 'hr'
        ordering = ['date']

    title = models.ForeignKey(Title, related_name='title_compo_diffs')
    role = models.ForeignKey(Role, related_name='title_compo_diffs')
    # true if role is new in title, false if role was removed
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.DateTimeField(db_index=True, auto_now_add=True)

    DATE_FIELD = 'date' # used for garbage collection

    def __unicode__(self):
        if self.new: 
            return unicode(self.title) + u' gets ' + unicode(self.role)
        else: 
            return unicode(self.title) + u' looses ' + unicode(self.role)



#------------------------------------------------------------------------------
class TitleMemberDiff(models.Model):
    """
    Represents the change in the assignment of a Title to a Member
    """

    class Meta:
        app_label = 'hr'
        ordering = ['date']

    member = models.ForeignKey(Member, related_name='title_member_diffs')
    title = models.ForeignKey(Title, related_name='title_member_diffs')
    # true if title is new for member, false if title was removed
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.DateTimeField(db_index=True, auto_now_add=True)

    DATE_FIELD = 'date' # used for garbage collection

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
            return '<a href="/%s/members/%d/" class="member">???</a>' % (app_prefix, self.member_id)
