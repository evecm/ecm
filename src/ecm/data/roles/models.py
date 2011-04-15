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

__date__ = "2010-01-24"
__author__ = "diabeteman"

from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

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
    baseID = models.BigIntegerField(db_index=True, default=0)
    corpDate = models.DateTimeField(db_index=True, default=datetime.now())
    lastLogin = models.DateTimeField(db_index=True, default=datetime.now())
    lastLogoff = models.DateTimeField(db_index=True, default=datetime.now())
    location = models.CharField(max_length=256, default="???")
    # TODO locationID = models.IntegerField(default=0)
    ship = models.CharField(max_length=128, default="???")
    accessLvl = models.PositiveIntegerField(default=0)
    corped = models.BooleanField(default=True)

    def get_implied_roles(self):
        """
        Retrieve all Roles assigned to one Member directly or through Titles
        """
        roles = self.roles
        for t in self.titles:
            roles |= t.titles
        
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
    
    def as_html(self):
        return '<a href="%s" class="member">%s</a>' % (self.get_url(), self.name)
    
    def __hash__(self):
        return self.characterID

    def __cmp__(self, other):
        return cmp(self.name.lower(), other.name.lower())

    def __unicode__(self):
        return self.name


#------------------------------------------------------------------------------
class RoleType(models.Model):
    """
    Category of Role
    """
    typeName = models.CharField(max_length=64, unique=True)
    dispName = models.CharField(max_length=64)
    
    def get_url(self):
        return '/roles/%s' % self.typeName
    
    def as_html(self):
        return '<a href="%s" class="role_type">%s</a>' % (self.get_url(), self.dispName)
    
    def __hash__(self):
        return self.id
    
    def __unicode__(self):
        if self.dispName:
            return self.dispName
        else:
            return self.typeName

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
    roleID = models.IntegerField()
    roleName = models.CharField(max_length=64)
    dispName = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    hangar = models.ForeignKey(Hangar, null=True, blank=True)
    wallet = models.ForeignKey(Wallet, null=True, blank=True)
    accessLvl = models.PositiveSmallIntegerField(default=0)
    
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
        
#    def getTitles(self):
#        """
#        Returns all the corporation Titles that contain this Role.
#        """
#        ids = TitleComposition.objects.filter(role=self).values_list("title", flat=True)
#        return Title.objects.filter(titleID__in=ids)
    
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
    
    def as_html(self):
        try:
            return '<a href="%s" class="role">%s</a>' % (self.get_url(), self.get_disp_name())
        except:
            return '<b>%s</b>' % self.get_disp_name()
    
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
    accessLvl = models.PositiveIntegerField(default=0)

    members = models.ManyToManyField(Member, through='TitleMembership', related_name="titles")
    roles = models.ManyToManyField(Role, through='TitleComposition', related_name="titles")

    def get_access_lvl(self):
        lvl = 0
        for r in self.roles.all() : 
            lvl += r.get_access_lvl()
        return lvl
    
    def get_url(self):
        return '/titles/%d' % self.titleID
    
    def as_html(self):
        return '<a href="%s" class="title">%s</a>' % (self.get_url(), self.titleName)
    
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
    
    h = None

    def __hash__(self):
        if not self.h:
            try:    self.h = self.member.characterID * 1000 + self.role.id
            except: self.h = -1
        return self.h
    
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
    
    h = None
        
    def __hash__(self):
        if not self.h:
            try:
                self.h = self.member.characterID * 100000 + self.title.titleID
            except:
                self.h = -1
        return self.h
    
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
    
    h = None
    
    def __hash__(self):
        if not self.h:
            self.h = self.title.titleID * 1000 + self.role.id 
        return self.h 
    
    def __unicode__(self):
        return unicode(self.title) + u' has ' + unicode(self.role)


#------------------------------------------------------------------------------
class CharacterOwnership(models.Model):
    """
    Associates EVE characters to ECM Users
    """
    user = models.ForeignKey(User)
    character = models.OneToOneField(Member, related_name="owner")
    is_main_character = models.BooleanField(default=False)

    def owner_url(self):
        return '/users/%d' % self.user_id
    
    def character_url(self):
        return '/members/%d' % self.character_id
    
    def user_as_html(self):
        return '<a href="%s" class="user">%s</a>' % (self.owner_url(), self.user.username)
    
    def character_as_html(self):
        return '<a href="%s" class="member">%s</a>' % (self.character_url(), self.character.name)
        
    def main_or_alt_admin_display(self):
        if self.is_main_character:
            return "Main"
        else:
            return "Alt"
    main_or_alt_admin_display.short_description = "Type"
    
    def __unicode__(self):
        try:
            return "%s owns %s" % (self.user.username, self.character.name)
        except:
            return "%d owns %d" % (self.user_id, self.character_id)

#------------------------------------------------------------------------------
class TitleCompoDiff(models.Model):
    """
    Represents the unitary modification of a Title (added or removed Role)
    """
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
    characterID = models.BigIntegerField(db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    nickname = models.CharField(max_length=256, db_index=True)
    # true if member has been corped. False if he/she has leaved the corporation
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.DateTimeField(db_index=True, default=datetime.now())
    
    def __unicode__(self):
        if self.new: return '%s corped' % self.name
        else       : return '%s leaved' % self.name
        
#------------------------------------------------------------------------------
class TitleMemberDiff(models.Model):
    """
    Represents the change in the assignment of a Title to a Member
    """
    member = models.ForeignKey(Member)
    title = models.ForeignKey(Title)
    # true if title is new for member, false if title was removed
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.DateTimeField(db_index=True, default=datetime.now())

    def member_as_html(self):
        try:
            return self.member.as_html()
        except:
            # this could fail if the RoleMemberDiff has been recorded from
            # /corp/MemberSecurity.xml.aspx but that the member has not been
            # parsed from /corp/MemberTracking.xml.aspx yet
            return '<a href="/members/%d" class="member">???</a>' % self.member_id

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
    member = models.ForeignKey(Member)
    role = models.ForeignKey(Role)
    # true if role is new for member, false if role was removed
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.DateTimeField(db_index=True, default=datetime.now())
    
    def member_as_html(self):
        try:
            return self.member.as_html()
        except: 
            # this could fail if the RoleMemberDiff has been recorded from
            # /corp/MemberSecurity.xml.aspx but that the member has not been
            # parsed from /corp/MemberTracking.xml.aspx yet
            return '<a href="/members/%d" class="member">???</a>' % self.member_id
    
    def __unicode__(self):
        try: 
            membername = self.member.name
        except: 
            membername = str(self.member_id)
        if self.new: return '%s got %s' % (membername, self.role.name)
        else       : return '%s lost %s' % (membername, self.role.name)

