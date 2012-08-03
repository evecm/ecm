#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.utils import timezone

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'APIKey'
        db.create_table('common_apikey', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('keyID', self.gf('django.db.models.fields.IntegerField')()),
            ('characterID', self.gf('django.db.models.fields.IntegerField')()),
            ('vCode', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('common', ['APIKey']) 

        # Adding model 'UserAPIKey'
        db.create_table('common_userapikey', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='eve_accounts', to=orm['auth.User'])),
            ('keyID', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('vCode', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_valid', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('common', ['UserAPIKey'])

        # Adding model 'ExternalApplication'
        db.create_table('common_externalapplication', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=1024)),
        ))
        db.send_create_signal('common', ['ExternalApplication'])

        # Adding model 'UserBinding'
        db.create_table('common_userbinding', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bindings', to=orm['auth.User'])),
            ('external_app', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_bindings', to=orm['common.ExternalApplication'])),
            ('external_id', self.gf('django.db.models.fields.IntegerField')()),
            ('external_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('common', ['UserBinding'])

        # Adding model 'GroupBinding'
        db.create_table('common_groupbinding', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bindings', to=orm['auth.Group'])),
            ('external_app', self.gf('django.db.models.fields.related.ForeignKey')(related_name='group_bindings', to=orm['common.ExternalApplication'])),
            ('external_id', self.gf('django.db.models.fields.IntegerField')()),
            ('external_name', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('common', ['GroupBinding'])

        # Adding model 'UpdateDate'
        db.create_table('common_updatedate', (
            ('model_name', self.gf('django.db.models.fields.CharField')(max_length=64, primary_key=True)),
            ('update_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('prev_update', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('common', ['UpdateDate'])

        # Adding model 'ColorThreshold'
        db.create_table('common_colorthreshold', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('color', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('threshold', self.gf('django.db.models.fields.BigIntegerField')()),
        ))
        db.send_create_signal('common', ['ColorThreshold'])

        # Adding model 'UrlPermission'
        db.create_table('common_urlpermission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pattern', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('common', ['UrlPermission'])

        # Adding M2M table for field groups on 'UrlPermission'
        db.create_table('common_urlpermission_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('urlpermission', models.ForeignKey(orm['common.urlpermission'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('common_urlpermission_groups', ['urlpermission_id', 'group_id'])

        # Adding model 'RegistrationProfile'
        db.create_table('common_registrationprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('activation_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('common', ['RegistrationProfile'])


    def backwards(self, orm):
        
        # Deleting model 'APIKey'
        db.delete_table('common_apikey')

        # Deleting model 'UserAPIKey'
        db.delete_table('common_userapikey')

        # Deleting model 'ExternalApplication'
        db.delete_table('common_externalapplication')

        # Deleting model 'UserBinding'
        db.delete_table('common_userbinding')

        # Deleting model 'GroupBinding'
        db.delete_table('common_groupbinding')

        # Deleting model 'UpdateDate'
        db.delete_table('common_updatedate')

        # Deleting model 'ColorThreshold'
        db.delete_table('common_colorthreshold')

        # Deleting model 'UrlPermission'
        db.delete_table('common_urlpermission')

        # Removing M2M table for field groups on 'UrlPermission'
        db.delete_table('common_urlpermission_groups')

        # Deleting model 'RegistrationProfile'
        db.delete_table('common_registrationprofile')


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'timezone.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'timezone.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'common.apikey': {
            'Meta': {'object_name': 'APIKey'},
            'characterID': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyID': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'vCode': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'common.colorthreshold': {
            'Meta': {'object_name': 'ColorThreshold'},
            'color': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'threshold': ('django.db.models.fields.BigIntegerField', [], {})
        },
        'common.externalapplication': {
            'Meta': {'object_name': 'ExternalApplication'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        'common.groupbinding': {
            'Meta': {'object_name': 'GroupBinding'},
            'external_app': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_bindings'", 'to': "orm['common.ExternalApplication']"}),
            'external_id': ('django.db.models.fields.IntegerField', [], {}),
            'external_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bindings'", 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'common.registrationprofile': {
            'Meta': {'object_name': 'RegistrationProfile'},
            'activation_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'common.updatedate': {
            'Meta': {'object_name': 'UpdateDate'},
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'}),
            'prev_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'update_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        'common.urlpermission': {
            'Meta': {'object_name': 'UrlPermission'},
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'allowed_urls'", 'symmetrical': 'False', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pattern': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'common.userapikey': {
            'Meta': {'object_name': 'UserAPIKey'},
            'is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'keyID': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'eve_accounts'", 'to': "orm['auth.User']"}),
            'vCode': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'common.userbinding': {
            'Meta': {'object_name': 'UserBinding'},
            'external_app': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_bindings'", 'to': "orm['common.ExternalApplication']"}),
            'external_id': ('django.db.models.fields.IntegerField', [], {}),
            'external_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bindings'", 'to': "orm['auth.User']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['common']
