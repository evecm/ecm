'''
This file is part of ICE Security Management

Created on 24 jan. 2010
@author: diabeteman
'''

from ISM.corp.models import Hangar, Wallet

from django.db import models

#______________________________________________________________________________
class Member(models.Model):
    characterID = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100, db_index=True)
    nickname = models.CharField(max_length=256, default="")
    baseID = models.BigIntegerField(db_index=True, default=0)
    corpDate = models.BigIntegerField(db_index=True, default=0)
    lastLogin = models.BigIntegerField(db_index=True, default=0)
    lastLogoff = models.BigIntegerField(db_index=True, default=0)
    locationID = models.IntegerField()
    ship = models.CharField(max_length=100, default="")

    def __eq__(self, other):
        return self.characterID == other.characterID

    def __unicode__(self):
        return self.name



#______________________________________________________________________________
class RoleType(models.Model):
    typeName = models.CharField(max_length=64, unique=True)
    dispName = models.CharField(max_length=64)
    
    def __eq__(self, other):
        return self.id == other.id

    def __unicode__(self):
        if self.dispName:
            return self.dispName
        else:
            return self.typeName
    
#______________________________________________________________________________
class Title(models.Model):
    titleID = models.IntegerField(primary_key=True)
    titleName = models.CharField(max_length=256)
    members = models.ManyToManyField(Member, through='TitleMembership')
    tiedToBase = models.IntegerField(default=0)
    
    def __eq__(self, other):
        return self.titleID == other.titleID
    
    def __unicode__(self):
        return self.titleName
    
#______________________________________________________________________________
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
    
    def __eq__(self, other):
        return self.id == other.id

    def __unicode__(self):
        name = self.dispName or self.roleName
        division = None
        if self.hangar:
            division = ' on ' + self.hangar.name
        elif self.wallet:
            division = ' on ' + self.wallet.name
        return name + (division or '') + ' -- ' + unicode(self.roleType)
    
#______________________________________________________________________________
class RoleMembership(models.Model):
    member = models.ForeignKey(Member)
    role = models.ForeignKey(Role)
    
    def __eq__(self, other):
        return self.member == other.member and self.role == other.role
    
    def __unicode__(self):
        return unicode(self.member) + u' has ' + unicode(self.role)
    
#______________________________________________________________________________
class TitleMembership(models.Model):
    member = models.ForeignKey(Member)
    title = models.ForeignKey(Title)

    def __eq__(self, other):
        return self.member == other.member and self.title == other.title
    
    def __unicode__(self):
        return unicode(self.member) + u' is ' + unicode(self.title)
    
#______________________________________________________________________________
class TitleComposition(models.Model):
    title = models.ForeignKey(Title)
    role = models.ForeignKey(Role)
    
    def __eq__(self, other):
        return self.title.titleID == other.title.titleID and self.role.id == other.role.id
    
    def __unicode__(self):
        return unicode(self.title) + u' has ' + unicode(self.role)


#========================#
#  DIFF HISTORY CLASSES  #
#========================#
#______________________________________________________________________________
class TitleCompoDiff(models.Model):
    title = models.ForeignKey(Title)
    role = models.ForeignKey(Role)
    # true if role is new in title, false if role was removed
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.BigIntegerField(db_index=True, default=0)
    
    def __unicode__(self):
        if self.new: return unicode(self.title) + u' gets ' + unicode(self.role)
        else       : return unicode(self.title) + u' looses ' + unicode(self.role)
        
#______________________________________________________________________________
class MemberDiff(models.Model):
    characterID = models.BigIntegerField(db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    nickname = models.CharField(max_length=256, db_index=True)
    # true if title is new for member, false if title was removed
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.BigIntegerField(db_index=True, default=0)
    
    def __unicode__(self):
        if self.new: return '%s corped' % self.name
        else       : return '%s leaved' % self.name
        
#______________________________________________________________________________
class TitleMemberDiff(models.Model):
    member = models.ForeignKey(Member)
    title = models.ForeignKey(Title)
    # true if title is new for member, false if title was removed
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.BigIntegerField(db_index=True, default=0)

    def __unicode__(self):
        return unicode(self.member) + u' is ' + unicode(self.title)
    
#______________________________________________________________________________
class RoleMemberDiff(models.Model):
    member = models.ForeignKey(Member)
    role = models.ForeignKey(Role)
    # true if role is new for member, false if role was removed
    new = models.BooleanField(db_index=True, default=True)
    # date of change
    date = models.BigIntegerField(db_index=True, default=0)

    def __unicode__(self):
        return unicode(self.member) + u' has ' + unicode(self.role)
    