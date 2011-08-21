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

from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

from ecm.lib import bigintpatch
from ecm.data.corp.models import Hangar, Wallet

#------------------------------------------------------------------------------
class Member(models.Model):
    """
    Member of the corporation
    """
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

    def get_implied_roles(self):
        """
        Retrieve all Roles assigned to one Member directly or through Titles
        """
        roles = self.roles.all()
        for t in self.titles.all():
            roles |= t.roles.all()
        return roles.distinct()
    
    def is_director(self):
        """
        True if the Member has the role 'Director'
        """
        return self.roles.filter(roleID=1).count() > 0
    
    def get_access_lvl(self):
        """
        Calculates the security access level of a member. 
        It is the sum of single access levels of each Role assigned to him/her.
        """
        lvl = 0
        if self.is_director():
            lvl = Member.DIRECTOR_ACCESS_LVL
        else:
            roles = self.get_implied_roles()
            for r in roles: 
                lvl += r.get_access_lvl()
        return lvl
    
    def get_url(self):
        return '/members/%d' % self.characterID
    
    def permalink(self):
        return '<a href="%s" class="member">%s</a>' % (self.get_url(), self.name)
        
    def owner_url(self):
        if self.owner_id:
            return '/players/%d' % self.owner_id
        else:
            return None
    
    def owner_permalink(self):
        url = self.owner_url()
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
class RoleType(models.Model):
    """
    Category of Role
    """
    typeName = models.CharField(max_length=64, unique=True)
    dispName = models.CharField(max_length=64)
    
    def get_url(self):
        return '/roles/%s' % self.typeName
    
    def permalink(self):
        return '<a href="%s" class="role_type">%s</a>' % (self.get_url(), self.dispName)
    
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
        if self.hangar:
            return self.hangar.accessLvl
        elif self.wallet:
            return self.wallet.accessLvl
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
        try:
            name = self.dispName
            if self.hangar_id :
                name = name % Hangar.objects.get(hangarID=self.hangar_id).name
            elif self.wallet_id : 
                name = name % Wallet.objects.get(walletID=self.wallet_id).name
            return name
        except:
            return self.roleName
        
    def get_url(self):
        return '/roles/%s/%d' % (self.roleType.typeName, self.roleID)
    
    def permalink(self):
        try:
            return '<a href="%s" class="role">%s</a>' % (self.get_url(), self.get_disp_name())
        except:
            return '<b>%s</b>' % self.get_disp_name()
    
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return self.id
    
    def __unicode__(self):
        try:
            name = self.dispName
            if self.hangar_id :
                name = name % Hangar.objects.get(hangarID=self.hangar_id).name
            elif self.wallet_id : 
                name = name % Wallet.objects.get(walletID=self.wallet_id).name
            return "%s - %s" % (name, unicode(self.roleType))
        except:
            return self.roleName
    
    def __getattr__(self, attr_name):
        if attr_name == "name":
            return self.get_disp_name()
        else:
            raise AttributeError("Role has no attribute %s" % attr_name)
    



#------------------------------------------------------------------------------
class Title(models.Model):
    """
    Corporation Title. Titles are an aggregation of multiple Roles
    """
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
    
    def get_url(self):
        return '/titles/%d' % self.titleID
    
    def permalink(self):
        return '<a href="%s" class="title">%s</a>' % (self.get_url(), self.titleName)
    
    def __eq__(self, other):
        return self.titleID == other.titleID
    
    def __hash__(self):
        return self.titleID
    
    def __unicode__(self):
        return self.titleName
    

#------------------------------------------------------------------------------
class RoleMembership(models.Model):
    """
    Represents the assignment of one Role to a Member.
    """
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
class TitleMembership(models.Model):
    """
    Represents the assignment of one Title to a Member.
    """
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
    title = models.ForeignKey(Title)
    role = models.ForeignKey(Role)
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __hash__(self):
        return self.title_id * 1000 + self.role_id
    
    def __unicode__(self):
        return unicode(self.title) + u' has ' + unicode(self.role)


#------------------------------------------------------------------------------
class CharacterOwnership(models.Model):
    """
    Associates EVE characters to ECM Users !!!! DEPRECATED !!!!
    """
    owner = models.ForeignKey(User, related_name="__characters")
    character = models.OneToOneField(Member, related_name="__ownership")
    is_main_character = models.BooleanField(default=False)

    def owner_url(self):
        return '/players/%d' % self.owner_id
    
    def owner_permalink(self):
        return '<a href="%s" class="player">%s</a>' % (self.owner_url(), self.owner.username)
    
    def main_or_alt_admin_display(self):
        if self.is_main_character:
            return "Main"
        else:
            return "Alt"
    main_or_alt_admin_display.short_description = "Type"
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __hash__(self):
        return self.character_id * 10000 + self.owner_id
    
    def __unicode__(self):
        try:
            return "%s owns %s" % (self.owner.username, self.character.name)
        except:
            return "%d owns %d" % (self.owner_id, self.character_id)

#------------------------------------------------------------------------------
class TitleCompoDiff(models.Model):
    """
    Represents the unitary modification of a Title (added or removed Role)
    """
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
class MemberDiff(models.Model):
    """
    Represents the arrival or departure of a member of the corporation
    """
    id = bigintpatch.BigAutoField(primary_key=True)
    member = models.ForeignKey(Member, related_name="diffs")
    name = models.CharField(max_length=100, db_index=True)
    nickname = models.CharField(max_length=256, db_index=True)
    # true if member has been corped. False if he/she has leaved the corporation
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.DateTimeField(db_index=True, default=datetime.now())
    
    def get_url(self):
        return '/members/%d' % self.member_id
    
    def permalink(self):
        return '<a href="%s" class="member">%s</a>' % (self.get_url(), self.name) 
    
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return self.id
    
    def __unicode__(self):
        if self.new: return '%s corped' % self.name
        else       : return '%s leaved' % self.name
        
#------------------------------------------------------------------------------
class TitleMemberDiff(models.Model):
    """
    Represents the change in the assignment of a Title to a Member
    """
    id = bigintpatch.BigAutoField(primary_key=True)
    member = models.ForeignKey(Member)
    title = models.ForeignKey(Title)
    # true if title is new for member, false if title was removed
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.DateTimeField(db_index=True, default=datetime.now())

    def access_permalink(self):
        return self.title.permalink()
    
    def member_permalink(self):
        try:
            return self.member.permalink()
        except:
            # this could fail if the RoleMemberDiff has been recorded from
            # /corp/MemberSecurity.xml.aspx but that the member has not been
            # parsed from /corp/MemberTracking.xml.aspx yet
            return '<a href="/members/%d" class="member">???</a>' % self.member_id
    
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
    
#------------------------------------------------------------------------------
class RoleMemberDiff(models.Model):
    """
    Represents the change in the assignment of a Role to a Member
    """
    id = bigintpatch.BigAutoField(primary_key=True)
    member = models.ForeignKey(Member)
    role = models.ForeignKey(Role)
    # true if role is new for member, false if role was removed
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.DateTimeField(db_index=True, default=datetime.now())
    
    def access_permalink(self):
        return self.role.permalink()
    
    def member_permalink(self):
        try:
            return self.member.permalink()
        except: 
            # this could fail if the RoleMemberDiff has been recorded from
            # /corp/MemberSecurity.xml.aspx but that the member has not been
            # parsed from /corp/MemberTracking.xml.aspx yet
            return '<a href="/members/%d" class="member">???</a>' % self.member_id
    
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return self.id
    
    def __unicode__(self):
        try: 
            membername = self.member.name
        except: 
            membername = str(self.member_id)
        if self.new: return '%s got %s' % (membername, self.role.name)
        else       : return '%s lost %s' % (membername, self.role.name)

