# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class Migration(DataMigration):

    def forwards(self, orm):
        """
        Copy all the association data from CharacterOwnership into the Member 'owner' field.
        """
        for m in orm.Member.objects.all():
            try:
                owner = orm.CharacterOwnership.objects.get(character=m).owner
            except ObjectDoesNotExist:
                owner = None
            m.owner = owner
            m.save()
        orm.CharacterOwnership.objects.all().delete()
        

    def backwards(self, orm):
        """
        Copy all the association data from Member to CharacterOwnership objects.
        """
        for m in orm.Member.objects.all():
            if m.owner is not None:
                orm.CharacterOwnership.objects.create(owner=m.owner, character=m)
                m.owner = None

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'corp.hangar': {
            'Meta': {'object_name': 'Hangar'},
            'accessLvl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'hangarID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'corp.wallet': {
            'Meta': {'object_name': 'Wallet'},
            'accessLvl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'walletID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'})
        },
        'roles.characterownership': {
            'Meta': {'object_name': 'CharacterOwnership'},
            'character': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'__ownership'", 'unique': 'True', 'to': "orm['roles.Member']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_main_character': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'__characters'", 'to': "orm['auth.User']"})
        },
        'roles.member': {
            'Meta': {'object_name': 'Member'},
            'accessLvl': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'baseID': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'characterID': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'corpDate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 7, 31, 20, 40, 16, 828000)'}),
            'corped': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'lastLogin': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 7, 31, 20, 40, 16, 828000)'}),
            'lastLogoff': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 7, 31, 20, 40, 16, 828000)'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "'???'", 'max_length': '256'}),
            'locationID': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'characters'", 'null': 'True', 'to': "orm['auth.User']"}),
            'ship': ('django.db.models.fields.CharField', [], {'default': "'???'", 'max_length': '128'})
        },
        'roles.memberdiff': {
            'Meta': {'object_name': 'MemberDiff'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 7, 31, 20, 40, 16, 831000)', 'db_index': 'True'}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'diffs'", 'to': "orm['roles.Member']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'new': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'})
        },
        'roles.role': {
            'Meta': {'object_name': 'Role'},
            'accessLvl': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'dispName': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'hangar': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corp.Hangar']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'roles'", 'symmetrical': 'False', 'through': "orm['roles.RoleMembership']", 'to': "orm['roles.Member']"}),
            'roleID': ('django.db.models.fields.BigIntegerField', [], {}),
            'roleName': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'roleType': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': "orm['roles.RoleType']"}),
            'wallet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corp.Wallet']", 'null': 'True', 'blank': 'True'})
        },
        'roles.rolememberdiff': {
            'Meta': {'object_name': 'RoleMemberDiff'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 7, 31, 20, 40, 16, 832000)', 'db_index': 'True'}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['roles.Member']"}),
            'new': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['roles.Role']"})
        },
        'roles.rolemembership': {
            'Meta': {'object_name': 'RoleMembership'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['roles.Member']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['roles.Role']"})
        },
        'roles.roletype': {
            'Meta': {'object_name': 'RoleType'},
            'dispName': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'typeName': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'roles.title': {
            'Meta': {'object_name': 'Title'},
            'accessLvl': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'titles'", 'symmetrical': 'False', 'through': "orm['roles.TitleMembership']", 'to': "orm['roles.Member']"}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'titles'", 'symmetrical': 'False', 'through': "orm['roles.TitleComposition']", 'to': "orm['roles.Role']"}),
            'tiedToBase': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'titleID': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'titleName': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'roles.titlecompodiff': {
            'Meta': {'object_name': 'TitleCompoDiff'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 7, 31, 20, 40, 16, 831000)', 'db_index': 'True'}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'new': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['roles.Role']"}),
            'title': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['roles.Title']"})
        },
        'roles.titlecomposition': {
            'Meta': {'object_name': 'TitleComposition'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['roles.Role']"}),
            'title': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['roles.Title']"})
        },
        'roles.titlememberdiff': {
            'Meta': {'object_name': 'TitleMemberDiff'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 7, 31, 20, 40, 16, 832000)', 'db_index': 'True'}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['roles.Member']"}),
            'new': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'title': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['roles.Title']"})
        },
        'roles.titlemembership': {
            'Meta': {'object_name': 'TitleMembership'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['roles.Member']"}),
            'title': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['roles.Title']"})
        }
    }

    complete_apps = ['roles']
