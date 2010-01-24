from django.db import models

#______________________________________________________________________________
class Character(models.Model):
    characterID = models.IntegerField(primary_key = True)
    name = models.CharField(max_length = 100)
    
    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

#______________________________________________________________________________
class RoleType(models.Model):
    typeName = models.CharField(max_length = 64)
    
    def __unicode__(self):
        return self.typeName
    def __str__(self):
        return self.typeName

#______________________________________________________________________________
class Title(models.Model):
    titleID = models.IntegerField(primary_key = True)
    titleName = models.CharField(max_length=256)
    members = models.ManyToManyField(Character, through='TitleMembership')
    
    def __unicode__(self):
        return self.titleName
    def __str__(self):
        return self.titleName
    class Meta:
        ordering = ['titleID']
#______________________________________________________________________________
class Role(models.Model):
    roleType = models.ForeignKey(RoleType, db_index = True)
    roleID = models.IntegerField()
    roleName = models.CharField(max_length=64)
    members = models.ManyToManyField(Character, through='RoleMembership')
    titles = models.ManyToManyField(Title, through='TitleComposition')
    description = models.CharField(max_length=256)
    
    def __unicode__(self):
        return unicode(self.roleName) + u'/' + unicode(self.roleType)
    def __str__(self):
        return str(self.roleName) + '/' + str(self.roleType)
    class Meta:
        ordering = ['roleType', 'roleID']
#______________________________________________________________________________
class RoleMembership(models.Model):
    character = models.ForeignKey(Character)
    role = models.ForeignKey(Role)
    
    def __unicode__(self):
        return unicode(self.character) + u' has ' + unicode(self.role)
    def __str__(self):
        return str(self.roleName) + ' has ' + str(self.role)
#______________________________________________________________________________
class TitleMembership(models.Model):
    character = models.ForeignKey(Character)
    title = models.ForeignKey(Title)
    
    def __unicode__(self):
        return unicode(self.character) + u' is ' + unicode(self.title)
    def __str__(self):
        return str(self.character) + ' is ' + str(self.title)
    
#______________________________________________________________________________
class TitleComposition(models.Model):
    title = models.ForeignKey(Title)
    role = models.ForeignKey(Role)

    def __unicode__(self):
        return unicode(self.title) + u' has ' + unicode(self.role)
    def __str__(self):
        return str(self.title) + ' has ' + str(self.role)
    
    