"""
The MIT License - EVE Corporation Management

Copyright (c) 2010 Robin Jarry

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

__date__ = "2010-01-24"
__author__ = "diabeteman"



from ecm.data.corp.models import Hangar, Wallet

from django.db import models
from datetime import datetime

#------------------------------------------------------------------------------
class Member(models.Model):
    
    DIRECTOR_ACCESS_LVL = 999999999999;

    characterID = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=128, db_index=True)
    nickname = models.CharField(max_length=256, default="")
    baseID = models.BigIntegerField(db_index=True, default=0)
    corpDate = models.DateTimeField(db_index=True, default=datetime.now())
    lastLogin = models.DateTimeField(db_index=True, default=datetime.now())
    lastLogoff = models.DateTimeField(db_index=True, default=datetime.now())
    location = models.CharField(max_length=256, default="")
    ship = models.CharField(max_length=128, default="")
    accessLvl = models.PositiveIntegerField(default=0)
    corped = models.BooleanField(default=True)
    extraRoles = models.PositiveIntegerField(default=0)

    def getTitles(self):
        ids = TitleMembership.objects.filter(member=self).values_list("title", flat=True)
        return Title.objects.filter(titleID__in=ids)
    
    def getRoles(self, ignore_director=False):
        if ignore_director:
            ids = RoleMembership.objects.filter(member=self).exclude(role__roleID=1).values_list("role", flat=True)
        else:
            ids = RoleMembership.objects.filter(member=self).values_list("role", flat=True)
        return Role.objects.filter(id__in=ids)
    
    def getImpliedRoles(self):
        roles = self.getRoles()
        for t in self.getTitles():
            roles |= t.getRoles()
        
        return roles.distinct()
    
    def isDirector(self):
        return RoleMembership.objects.filter(member=self, role__roleID=1).count() > 0
    
    def getAccessLvl(self):
        lvl = 0
        if self.isDirector():
            lvl = self.DIRECTOR_ACCESS_LVL
        else:
            roles = self.getImpliedRoles()
            for r in roles: 
                lvl += r.getAccessLvl()
        return lvl

    def getTitleChanges(self):
        return TitleMemberDiff.objects.filter(member=self).order_by("-id")
    
    def __hash__(self):
        return self.characterID

    def __eq__(self, other):
        return self.characterID == other.characterID
    
    def __cmp__(self, other):
        return cmp(self.name.lower(), other.name.lower())

    def __unicode__(self):
        return self.name


#------------------------------------------------------------------------------
class RoleType(models.Model):
    typeName = models.CharField(max_length=64, unique=True)
    dispName = models.CharField(max_length=64)
    
    def __hash__(self):
        return self.id
    
    def __eq__(self, other):
        return self.id == other.id

    def __unicode__(self):
        if self.dispName:
            return self.dispName
        else:
            return self.typeName
    
#------------------------------------------------------------------------------
class Title(models.Model):
    titleID = models.BigIntegerField(primary_key=True)
    titleName = models.CharField(max_length=256)
    members = models.ManyToManyField(Member, through='TitleMembership')
    tiedToBase = models.BigIntegerField(default=0)
    accessLvl = models.PositiveIntegerField(default=0)
    
    def getRoles(self):
        ids = TitleComposition.objects.filter(title=self).values_list("role", flat=True)
        return Role.objects.filter(id__in=ids)
        
    def getAccessLvl(self):
        roles = self.getRoles()
        lvl = 0
        for r in roles : lvl += r.getAccessLvl()
        return lvl
    
    def __hash__(self):
        return self.titleID
    
    def __eq__(self, other):
        return self.titleID == other.titleID
    
    def __unicode__(self):
        return self.titleName
    
#------------------------------------------------------------------------------
class Role(models.Model):
    roleType = models.ForeignKey(RoleType, db_index=True)
    roleID = models.IntegerField()
    roleName = models.CharField(max_length=64)
    dispName = models.CharField(max_length=64)
    members = models.ManyToManyField(Member, through='RoleMembership')
    titles = models.ManyToManyField(Title, through='TitleComposition')
    description = models.CharField(max_length=256)
    hangar = models.ForeignKey(Hangar, null=True, blank=True)
    wallet = models.ForeignKey(Wallet, null=True, blank=True)
    accessLvl = models.PositiveSmallIntegerField(default=0)
    
    def getAccessLvl(self):
        if   self.hangar: return self.hangar.accessLvl
        elif self.wallet: return self.wallet.accessLvl
        else:             return self.accessLvl
    
    def getMembersThroughTitles(self, with_direct_roles=False):
        if with_direct_roles:
            members = self.members.all()
        else:
            members = Member.objects.none()
        for title in self.titles.all(): 
            members |= title.members.all()
        return members.distinct()
            
    def __hash__(self):
        return self.id
    
    def __eq__(self, other):
        return self.id == other.id

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
            return self.getDispName()
        else:
            raise AttributeError("Role has no attribute %s" % attr_name)
    
    def getDispName(self):
        try:
            name = self.dispName
            if self.hangar_id :
                name = name % Hangar.objects.get(hangarID=self.hangar_id).name
            elif self.wallet_id : 
                name = name % Wallet.objects.get(walletID=self.wallet_id).name
            return name
        except:
            return self.roleName


#------------------------------------------------------------------------------
class RoleMembership(models.Model):
    member = models.ForeignKey(Member)
    role = models.ForeignKey(Role)
    
    h = None

    def __hash__(self):
        if not self.h:
            try:    self.h = self.member.characterID * self.role.id
            except: self.h = -1
        return self.h
    
    def __eq__(self, other):
        try: return self.member == other.member and self.role == other.role
        except: return False
    
    def __unicode__(self):
        try:
            return u'%s has %s (%s)' % (unicode(self.member), unicode(self.role), unicode(self.role.roleType))
        except:
            return u'member_id:%d has %s (%s)' % (self.member_id, unicode(self.role), unicode(self.role.roleType))
    
#------------------------------------------------------------------------------
class TitleMembership(models.Model):
    member = models.ForeignKey(Member)
    title = models.ForeignKey(Title)
    
    h = None
        
    def __hash__(self):
        if not self.h:
            try:
                self.h = self.member.characterID * self.title.titleID
            except:
                self.h = -1
        return self.h
    
    def __eq__(self, other):
        try: return self.member == other.member and self.title == other.title
        except: return False
    def __unicode__(self):
        try:
            return unicode(self.member) + u' is ' + unicode(self.title)
        except:
            return u'member_id:%d is %s' % (self.member_id, str(self.title))
    
#------------------------------------------------------------------------------
class TitleComposition(models.Model):
    title = models.ForeignKey(Title)
    role = models.ForeignKey(Role)
    
    h = None
    
    def __hash__(self):
        if not self.h:
            self.h = self.title.titleID + self.role.id 
        return self.h 
    
    def __eq__(self, other):
        return self.title.titleID == other.title.titleID and self.role.id == other.role.id
    
    def __unicode__(self):
        return unicode(self.title) + u' has ' + unicode(self.role)


#========================#
#  DIFF HISTORY CLASSES  #
#========================#
class Diff():

    def __getattr__(self, attr_name):
        try:
            return self.__dict__[attr_name]
        except KeyError:
            raise AttributeError("%s has no attribute %s" % (self.__class__.__name__, attr_name))


#------------------------------------------------------------------------------
class TitleCompoDiff(models.Model, Diff):
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
class MemberDiff(models.Model, Diff):
    characterID = models.BigIntegerField(db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    nickname = models.CharField(max_length=256, db_index=True)
    # true if title is new for member, false if title was removed
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.DateTimeField(db_index=True, default=datetime.now())
    
    def __unicode__(self):
        if self.new: return '%s corped' % self.name
        else       : return '%s leaved' % self.name
        
#------------------------------------------------------------------------------
class TitleMemberDiff(models.Model, Diff):
    member = models.ForeignKey(Member)
    title = models.ForeignKey(Title)
    # true if title is new for member, false if title was removed
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.DateTimeField(db_index=True, default=datetime.now())

    def __unicode__(self):
        try: 
            membername = self.member.name
        except: 
            membername = str(self.member_id)
        if self.new: return '%s got %s' % (membername, self.title.titleName)
        else       : return '%s lost %s' % (membername, self.title.titleName)
    
#------------------------------------------------------------------------------
class RoleMemberDiff(models.Model, Diff):
    member = models.ForeignKey(Member)
    role = models.ForeignKey(Role)
    # true if role is new for member, false if role was removed
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.DateTimeField(db_index=True, default=datetime.now())
    
    def __unicode__(self):
        try: 
            membername = self.member.name
        except: 
            membername = str(self.member_id)
        if self.new: return '%s got %s' % (membername, self.role.name)
        else       : return '%s lost %s' % (membername, self.role.name)

