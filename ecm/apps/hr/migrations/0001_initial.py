#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    depends_on = (
        ("corp", "0005_auto__add_corphangar__add_unique_corphangar_corp_hangar__add_corpwalle"),
    )
    
    def forwards(self, orm):
        from django.db import connection
        if 'roles_member' in connection.introspection.table_names():
            try:
                # if old "roles" app tables are found, rename them to "hr" tables
                db.rename_table('roles_member', 'hr_member')
                db.rename_table('roles_memberdiff', 'hr_memberdiff')

                db.rename_table('roles_roletype', 'hr_roletype')
                db.rename_table('roles_role', 'hr_role')
                db.rename_table('roles_rolemembership', 'hr_rolemembership')
                db.rename_table('roles_rolememberdiff', 'hr_rolememberdiff')

                db.rename_table('roles_title', 'hr_title')
                db.rename_table('roles_titlemembership', 'hr_titlemembership')
                db.rename_table('roles_titlecomposition', 'hr_titlecomposition')
                db.rename_table('roles_titlecompodiff', 'hr_titlecompodiff')
                db.rename_table('roles_titlememberdiff', 'hr_titlememberdiff')

                return
            except:
                # if tables not found, do the standard migration
                db.rollback_transaction()
                db.start_transaction()
        # Adding model 'Member'
        db.create_table('hr_member', (
            ('characterID', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(default='', max_length=256)),
            ('baseID', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('corpDate', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 10, 22, 12, 40, 4, 203014))),
            ('lastLogin', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 10, 22, 12, 40, 4, 203061))),
            ('lastLogoff', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 10, 22, 12, 40, 4, 203094))),
            ('locationID', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('location', self.gf('django.db.models.fields.CharField')(default='???', max_length=256, null=True, blank=True)),
            ('ship', self.gf('django.db.models.fields.CharField')(default='???', max_length=128)),
            ('accessLvl', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('corped', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='characters', null=True, to=orm['auth.User'])),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('hr', ['Member'])

        # Adding model 'MemberDiff'
        db.create_table('hr_memberdiff', (
            ('id', self.gf('ecm.lib.bigintpatch.BigAutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(related_name='diffs', to=orm['hr.Member'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=256, db_index=True)),
            ('new', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 10, 22, 12, 40, 4, 204283), db_index=True)),
        ))
        db.send_create_signal('hr', ['MemberDiff'])

        # Adding model 'RoleType'
        db.create_table('hr_roletype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('typeName', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('dispName', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('hr', ['RoleType'])

        # Adding model 'Role'
        db.create_table('hr_role', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('roleType', self.gf('django.db.models.fields.related.ForeignKey')(related_name='roles', to=orm['hr.RoleType'])),
            ('roleID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('roleName', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('dispName', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('hangar', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['corp.Hangar'], null=True, blank=True)),
            ('wallet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['corp.Wallet'], null=True, blank=True)),
            ('accessLvl', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
        ))
        db.send_create_signal('hr', ['Role'])

        # Adding model 'RoleMembership'
        db.create_table('hr_rolemembership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hr.Member'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hr.Role'])),
        ))
        db.send_create_signal('hr', ['RoleMembership'])

        # Adding model 'RoleMemberDiff'
        db.create_table('hr_rolememberdiff', (
            ('id', self.gf('ecm.lib.bigintpatch.BigAutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hr.Member'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hr.Role'])),
            ('new', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 10, 22, 12, 40, 4, 210650), db_index=True)),
        ))
        db.send_create_signal('hr', ['RoleMemberDiff'])

        # Adding model 'Title'
        db.create_table('hr_title', (
            ('titleID', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('titleName', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('tiedToBase', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('accessLvl', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
        ))
        db.send_create_signal('hr', ['Title'])

        # Adding model 'TitleMembership'
        db.create_table('hr_titlemembership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hr.Member'])),
            ('title', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hr.Title'])),
        ))
        db.send_create_signal('hr', ['TitleMembership'])

        # Adding model 'TitleComposition'
        db.create_table('hr_titlecomposition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hr.Title'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hr.Role'])),
        ))
        db.send_create_signal('hr', ['TitleComposition'])

        # Adding model 'TitleCompoDiff'
        db.create_table('hr_titlecompodiff', (
            ('id', self.gf('ecm.lib.bigintpatch.BigAutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hr.Title'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hr.Role'])),
            ('new', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 10, 22, 12, 40, 4, 216463), db_index=True)),
        ))
        db.send_create_signal('hr', ['TitleCompoDiff'])

        # Adding model 'TitleMemberDiff'
        db.create_table('hr_titlememberdiff', (
            ('id', self.gf('ecm.lib.bigintpatch.BigAutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hr.Member'])),
            ('title', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hr.Title'])),
            ('new', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 10, 22, 12, 40, 4, 217222), db_index=True)),
        ))
        db.send_create_signal('hr', ['TitleMemberDiff'])


    def backwards(self, orm):

        # Deleting model 'Member'
        db.delete_table('hr_member')

        # Deleting model 'MemberDiff'
        db.delete_table('hr_memberdiff')

        # Deleting model 'RoleType'
        db.delete_table('hr_roletype')

        # Deleting model 'Role'
        db.delete_table('hr_role')

        # Deleting model 'RoleMembership'
        db.delete_table('hr_rolemembership')

        # Deleting model 'RoleMemberDiff'
        db.delete_table('hr_rolememberdiff')

        # Deleting model 'Title'
        db.delete_table('hr_title')

        # Deleting model 'TitleMembership'
        db.delete_table('hr_titlemembership')

        # Deleting model 'TitleComposition'
        db.delete_table('hr_titlecomposition')

        # Deleting model 'TitleCompoDiff'
        db.delete_table('hr_titlecompodiff')

        # Deleting model 'TitleMemberDiff'
        db.delete_table('hr_titlememberdiff')


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 10, 22, 12, 40, 4, 203014)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 10, 22, 12, 40, 4, 203014)'}),
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
            'Meta': {'ordering': "['hangarID']", 'object_name': 'Hangar'},
            'accessLvl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'hangarID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'corp.wallet': {
            'Meta': {'ordering': "['walletID']", 'object_name': 'Wallet'},
            'accessLvl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'walletID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'})
        },
        'hr.member': {
            'Meta': {'ordering': "['name']", 'object_name': 'Member'},
            'accessLvl': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'baseID': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'characterID': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'corpDate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 10, 22, 12, 40, 4, 203014)'}),
            'corped': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'lastLogin': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 10, 22, 12, 40, 4, 203061)'}),
            'lastLogoff': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 10, 22, 12, 40, 4, 203094)'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "'???'", 'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'locationID': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'characters'", 'null': 'True', 'to': "orm['auth.User']"}),
            'ship': ('django.db.models.fields.CharField', [], {'default': "'???'", 'max_length': '128'})
        },
        'hr.memberdiff': {
            'Meta': {'ordering': "['date']", 'object_name': 'MemberDiff'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 10, 22, 12, 40, 4, 204283)', 'db_index': 'True'}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'diffs'", 'to': "orm['hr.Member']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'new': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'})
        },
        'hr.role': {
            'Meta': {'ordering': "['id']", 'object_name': 'Role'},
            'accessLvl': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'dispName': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'hangar': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corp.Hangar']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'roles'", 'symmetrical': 'False', 'through': "orm['hr.RoleMembership']", 'to': "orm['hr.Member']"}),
            'roleID': ('django.db.models.fields.BigIntegerField', [], {}),
            'roleName': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'roleType': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': "orm['hr.RoleType']"}),
            'wallet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corp.Wallet']", 'null': 'True', 'blank': 'True'})
        },
        'hr.rolememberdiff': {
            'Meta': {'ordering': "['date']", 'object_name': 'RoleMemberDiff'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 10, 22, 12, 40, 4, 210650)', 'db_index': 'True'}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Member']"}),
            'new': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Role']"})
        },
        'hr.rolemembership': {
            'Meta': {'ordering': "['member']", 'object_name': 'RoleMembership'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Member']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Role']"})
        },
        'hr.roletype': {
            'Meta': {'ordering': "['dispName']", 'object_name': 'RoleType'},
            'dispName': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'typeName': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'hr.title': {
            'Meta': {'ordering': "['titleID']", 'object_name': 'Title'},
            'accessLvl': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'titles'", 'symmetrical': 'False', 'through': "orm['hr.TitleMembership']", 'to': "orm['hr.Member']"}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'titles'", 'symmetrical': 'False', 'through': "orm['hr.TitleComposition']", 'to': "orm['hr.Role']"}),
            'tiedToBase': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'titleID': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'titleName': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'hr.titlecompodiff': {
            'Meta': {'ordering': "['date']", 'object_name': 'TitleCompoDiff'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 10, 22, 12, 40, 4, 216463)', 'db_index': 'True'}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'new': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Role']"}),
            'title': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Title']"})
        },
        'hr.titlecomposition': {
            'Meta': {'ordering': "['title']", 'object_name': 'TitleComposition'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Role']"}),
            'title': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Title']"})
        },
        'hr.titlememberdiff': {
            'Meta': {'ordering': "['date']", 'object_name': 'TitleMemberDiff'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 10, 22, 12, 40, 4, 217222)', 'db_index': 'True'}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Member']"}),
            'new': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'title': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Title']"})
        },
        'hr.titlemembership': {
            'Meta': {'ordering': "['member']", 'object_name': 'TitleMembership'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Member']"}),
            'title': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Title']"})
        }
    }

    complete_apps = ['hr']
