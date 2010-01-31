'''
This file is part of ICE Security Management

Created on 24 janv. 2010
@author: diabeteman
'''

from django.db import models

#______________________________________________________________________________
class Character(models.Model):
    characterID = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, db_index=True)
    nickname = models.CharField(max_length=256)
    baseID = models.IntegerField(db_index=True)
    corpDate = models.DateTimeField(db_index=True)
    lastLogin = models.DateTimeField(db_index=True)

    def __unicode__(self):
        return self.name
    
#______________________________________________________________________________
class Hangar(models.Model):
    hangarID = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name

#______________________________________________________________________________
class RoleType(models.Model):
    typeName = models.CharField(max_length=64, unique=True)

    def __unicode__(self):
        return self.typeName
    
#______________________________________________________________________________
class Title(models.Model):
    titleID = models.IntegerField(primary_key=True)
    titleName = models.CharField(max_length=256)
    members = models.ManyToManyField(Character, through='TitleMembership')
    tiedToBase = models.IntegerField(default=0)

    def __unicode__(self):
        return self.titleName
    
#______________________________________________________________________________
class Role(models.Model):
    roleType = models.ForeignKey(RoleType, db_index=True)
    roleID = models.IntegerField()
    roleName = models.CharField(max_length=64)
    members = models.ManyToManyField(Character, through='RoleMembership')
    titles = models.ManyToManyField(Title, through='TitleComposition')
    description = models.CharField(max_length=256)
    hangar = models.ForeignKey(Hangar, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.roleName) + (' on ' + self.hangar.name if self.hangar else '') + ' -- ' + unicode(self.roleType)
    
#______________________________________________________________________________
class RoleMembership(models.Model):
    character = models.ForeignKey(Character)
    role = models.ForeignKey(Role)

    def __unicode__(self):
        return unicode(self.character) + u' has ' + unicode(self.role)
    
#______________________________________________________________________________
class TitleMembership(models.Model):
    character = models.ForeignKey(Character)
    title = models.ForeignKey(Title)

    def __unicode__(self):
        return unicode(self.character) + u' is ' + unicode(self.title)
    
#______________________________________________________________________________
class TitleComposition(models.Model):
    title = models.ForeignKey(Title)
    role = models.ForeignKey(Role)

    def __unicode__(self):
        return unicode(self.title) + u' has ' + unicode(self.role)

