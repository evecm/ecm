# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Member'
        db.create_table('roles_member', (
            ('characterID', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(default='', max_length=256)),
            ('baseID', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('corpDate', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 7, 31, 4, 47, 53, 707000))),
            ('lastLogin', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 7, 31, 4, 47, 53, 707000))),
            ('lastLogoff', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 7, 31, 4, 47, 53, 707000))),
            ('locationID', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('location', self.gf('django.db.models.fields.CharField')(default='???', max_length=256)),
            ('ship', self.gf('django.db.models.fields.CharField')(default='???', max_length=128)),
            ('accessLvl', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('corped', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('roles', ['Member'])

        # Adding model 'RoleType'
        db.create_table('roles_roletype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('typeName', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('dispName', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('roles', ['RoleType'])

        # Adding model 'Role'
        db.create_table('roles_role', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('roleType', self.gf('django.db.models.fields.related.ForeignKey')(related_name='roles', to=orm['roles.RoleType'])),
            ('roleID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('roleName', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('dispName', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('hangar', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['corp.Hangar'], null=True, blank=True)),
            ('wallet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['corp.Wallet'], null=True, blank=True)),
            ('accessLvl', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
        ))
        db.send_create_signal('roles', ['Role'])

        # Adding model 'Title'
        db.create_table('roles_title', (
            ('titleID', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('titleName', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('tiedToBase', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('accessLvl', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
        ))
        db.send_create_signal('roles', ['Title'])

        # Adding model 'RoleMembership'
        db.create_table('roles_rolemembership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['roles.Member'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['roles.Role'])),
        ))
        db.send_create_signal('roles', ['RoleMembership'])

        # Adding model 'TitleMembership'
        db.create_table('roles_titlemembership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['roles.Member'])),
            ('title', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['roles.Title'])),
        ))
        db.send_create_signal('roles', ['TitleMembership'])

        # Adding model 'TitleComposition'
        db.create_table('roles_titlecomposition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['roles.Title'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['roles.Role'])),
        ))
        db.send_create_signal('roles', ['TitleComposition'])

        # Adding model 'CharacterOwnership'
        db.create_table('roles_characterownership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='characters', to=orm['auth.User'])),
            ('character', self.gf('django.db.models.fields.related.OneToOneField')(related_name='ownership', unique=True, to=orm['roles.Member'])),
            ('is_main_character', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('roles', ['CharacterOwnership'])

        # Adding model 'TitleCompoDiff'
        db.create_table('roles_titlecompodiff', (
            ('id', self.gf('ecm.lib.bigintpatch.BigAutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['roles.Title'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['roles.Role'])),
            ('new', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 7, 31, 4, 47, 53, 710000), db_index=True)),
        ))
        db.send_create_signal('roles', ['TitleCompoDiff'])

        # Adding model 'MemberDiff'
        db.create_table('roles_memberdiff', (
            ('id', self.gf('ecm.lib.bigintpatch.BigAutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(related_name='diffs', to=orm['roles.Member'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=256, db_index=True)),
            ('new', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 7, 31, 4, 47, 53, 711000), db_index=True)),
        ))
        db.send_create_signal('roles', ['MemberDiff'])

        # Adding model 'TitleMemberDiff'
        db.create_table('roles_titlememberdiff', (
            ('id', self.gf('ecm.lib.bigintpatch.BigAutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['roles.Member'])),
            ('title', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['roles.Title'])),
            ('new', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 7, 31, 4, 47, 53, 711000), db_index=True)),
        ))
        db.send_create_signal('roles', ['TitleMemberDiff'])

        # Adding model 'RoleMemberDiff'
        db.create_table('roles_rolememberdiff', (
            ('id', self.gf('ecm.lib.bigintpatch.BigAutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['roles.Member'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['roles.Role'])),
            ('new', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 7, 31, 4, 47, 53, 711000), db_index=True)),
        ))
        db.send_create_signal('roles', ['RoleMemberDiff'])


    def backwards(self, orm):
        
        # Deleting model 'Member'
        db.delete_table('roles_member')

        # Deleting model 'RoleType'
        db.delete_table('roles_roletype')

        # Deleting model 'Role'
        db.delete_table('roles_role')

        # Deleting model 'Title'
        db.delete_table('roles_title')

        # Deleting model 'RoleMembership'
        db.delete_table('roles_rolemembership')

        # Deleting model 'TitleMembership'
        db.delete_table('roles_titlemembership')

        # Deleting model 'TitleComposition'
        db.delete_table('roles_titlecomposition')

        # Deleting model 'CharacterOwnership'
        db.delete_table('roles_characterownership')

        # Deleting model 'TitleCompoDiff'
        db.delete_table('roles_titlecompodiff')

        # Deleting model 'MemberDiff'
        db.delete_table('roles_memberdiff')

        # Deleting model 'TitleMemberDiff'
        db.delete_table('roles_titlememberdiff')

        # Deleting model 'RoleMemberDiff'
        db.delete_table('roles_rolememberdiff')


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
            'character': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'ownership'", 'unique': 'True', 'to': "orm['roles.Member']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_main_character': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'characters'", 'to': "orm['auth.User']"})
        },
        'roles.member': {
            'Meta': {'object_name': 'Member'},
            'accessLvl': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'baseID': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'characterID': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'corpDate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 7, 31, 4, 47, 53, 707000)'}),
            'corped': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'lastLogin': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 7, 31, 4, 47, 53, 707000)'}),
            'lastLogoff': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 7, 31, 4, 47, 53, 707000)'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "'???'", 'max_length': '256'}),
            'locationID': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            'ship': ('django.db.models.fields.CharField', [], {'default': "'???'", 'max_length': '128'})
        },
        'roles.memberdiff': {
            'Meta': {'object_name': 'MemberDiff'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 7, 31, 4, 47, 53, 711000)', 'db_index': 'True'}),
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
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 7, 31, 4, 47, 53, 711000)', 'db_index': 'True'}),
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
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 7, 31, 4, 47, 53, 710000)', 'db_index': 'True'}),
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
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 7, 31, 4, 47, 53, 711000)', 'db_index': 'True'}),
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
