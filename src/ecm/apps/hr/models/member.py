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


from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

from ecm.core.eve.db import get_type_name

from ecm.lib import bigintpatch
from ecm.apps.hr import NAME as app_prefix

# little trick to change the Users' absolute urls
User.get_absolute_url = lambda self: '/hr/players/%s/' % self.id

#------------------------------------------------------------------------------
class Member(models.Model):
    """
    Member of the corporation
    """
    class Meta:
        app_label = 'hr'
        ordering = ['name']

    DIRECTOR_ACCESS_LVL = 999999999999

    characterID = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=128, db_index=True)
    nickname = models.CharField(max_length=256, default="")
    baseID = models.BigIntegerField(default=0)
    corpDate = models.DateTimeField(default=datetime.now())
    lastLogin = models.DateTimeField(default=datetime.now())
    lastLogoff = models.DateTimeField(default=datetime.now())
    locationID = models.IntegerField(db_index=True, default=0)
    location = models.CharField(max_length=256, default="???", null=True, blank=True)
    ship = models.CharField(max_length=128, default="???")
    accessLvl = models.BigIntegerField(default=0)
    corped = models.BooleanField(default=True)
    owner = models.ForeignKey(User, related_name='characters', null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    #Character Sheet
    DoB = models.CharField(max_length=128, null=True, blank=True)
    race = models.CharField(max_length=128, null=True, blank=True)
    bloodLine = models.CharField(max_length=128, null=True, blank=True)
    ancestry = models.CharField(max_length=128, null=True, blank=True)
    gender = models.CharField(max_length=128, null=True, blank=True)
    corporationName = models.CharField(max_length=128, null=True, blank=True)
    corporationID = models.IntegerField(null=True, blank=True)
    allianceName = models.CharField(max_length=128, null=True, blank=True)
    allianceID = models.IntegerField(blank=True, null=True)
    cloneName = models.CharField(max_length=128, null=True, blank=True)
    CloneSkillPoints = models.IntegerField(null=True, blank=True)
    balance = models.FloatField(default=0.0)
    memoryBonusName = models.CharField(max_length=128, blank=True, null=True)
    memoryBonusValue = models.IntegerField(blank=True, null=True)
    intelligenceBonusName = models.CharField(max_length=128, blank=True, null=True)
    intelligenceBonusValue = models.IntegerField(blank=True, null=True)
    charismaBonusName = models.CharField(max_length=128, blank=True, null=True)
    charismaBonusValue = models.IntegerField(blank=True, null=True)
    willpowerBonusName = models.CharField(max_length=128, blank=True, null=True)
    willpowerBonusValue = models.IntegerField(blank=True, null=True)
    perceptionBonusName = models.CharField(max_length=128, blank=True, null=True)
    perceptionBonusValue = models.IntegerField(blank=True, null=True)
    intelligence = models.IntegerField(default=0)
    memory = models.IntegerField(default=0)
    charisma = models.IntegerField(default=0)
    perception = models.IntegerField(default=0)
    willpower = models.IntegerField(default=0)
    
    def get_implied_roles(self):
        """
        Retrieve all Roles assigned to one Member directly or through Titles
        """
        roles = self.roles.all()
        for t in self.titles.all():
            roles |= t.roles.all()
        return roles.distinct()

    @property
    def is_director(self):
        """
        True if the Member has the role 'Director'
        """
        return self.roles.filter(roleID=1).exists()

    def get_access_lvl(self):
        """
        Calculates the security access level of a member.
        It is the sum of single access levels of each Role assigned to him/her.
        """
        lvl = 0
        if self.is_director:
            lvl = Member.DIRECTOR_ACCESS_LVL
        else:
            roles = self.get_implied_roles()
            for r in roles:
                lvl += r.get_access_lvl()
        return lvl

    @property
    def url(self):
        return '/%s/members/%d/' % (app_prefix, self.characterID)

    @property
    def permalink(self):
        return '<a href="%s" class="member">%s</a>' % (self.url, self.name)

    @property
    def owner_url(self):
        if self.owner_id:
            return '/%s/players/%d/' % (app_prefix, self.owner_id)
        else:
            return None

    @property
    def owner_permalink(self):
        url = self.owner_url
        if url is not None:
            return '<a href="%s" class="player">%s</a>' % (url, self.owner.username)
        else:
            return '<span class="error bold">no owner</span>'

    def __eq__(self, other):
        return self.characterID == other.characterID

    def __hash__(self):
        return self.characterID

    def __cmp__(self, other):
        return cmp(self.name.lower(), other.name.lower())

    def __unicode__(self):
        return unicode(self.name)

#------------------------------------------------------------------------------
class MemberDiff(models.Model):
    """
    Represents the arrival or departure of a member of the corporation
    """
    class Meta:
        app_label = 'hr'
        ordering = ['date']

    id = bigintpatch.BigAutoField(primary_key=True) #@ReservedAssignment
    member = models.ForeignKey(Member, related_name="diffs")
    name = models.CharField(max_length=100, db_index=True)
    nickname = models.CharField(max_length=256, db_index=True)
    # true if member has been corped. False if he/she has leaved the corporation
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.DateTimeField(db_index=True, default=datetime.now())

    @property
    def url(self):
        return '/%s/members/%d/' % (app_prefix, self.member_id)

    @property
    def permalink(self):
        return '<a href="%s" class="member">%s</a>' % (self.url, self.name)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

    def __unicode__(self):
        if self.new:
            return '%s corped' % self.name
        else:
            return '%s leaved' % self.name

#------------------------------------------------------------------------------
class MemberSession(models.Model):
    """
    Represents the arrival or departure of a member of the corporation
    """
    class Meta:
        app_label = 'hr'
        ordering = ['session_begin']

    id = bigintpatch.BigAutoField(primary_key=True) #@ReservedAssignment
    #TODO: somehow use FK's
    #member = models.ForeignKey(Member, related_name="diffs")
    #no defaults! forcing valid entries!
    character_id = models.BigIntegerField(db_index=True)
    session_begin = models.DateTimeField(db_index=True)
    session_end = models.DateTimeField()
    session_seconds = models.BigIntegerField(default=0)
    
    """
    @property
    def url(self):
        return '/%s/members/%d/' % (app_prefix, self.member_id)

    @property
    def permalink(self):
        return '<a href="%s" class="member">%s</a>' % (self.url, self.name)

    """
    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

#------------------------------------------------------------------------------
class Skill(models.Model):
    character = models.ForeignKey(Member, related_name = 'skills')
    typeID = models.IntegerField(default=0)
    skillpoints = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    def __unicode__(self):
        return self.name()
    def name(self):
        name = get_type_name(self.typeID)
        return unicode(name[0])