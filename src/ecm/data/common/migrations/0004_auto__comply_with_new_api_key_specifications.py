# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'APIKey.userID'
        db.delete_column('common_apikey', 'userID')

        # Deleting field 'APIKey.key'
        db.delete_column('common_apikey', 'key')

        # Deleting field 'APIKey.charID'
        db.delete_column('common_apikey', 'charID')

        # Adding field 'APIKey.keyID'
        db.add_column('common_apikey', 'keyID', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'APIKey.characterID'
        db.add_column('common_apikey', 'characterID', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'APIKey.vCode'
        db.add_column('common_apikey', 'vCode', self.gf('django.db.models.fields.CharField')(default="", max_length=255), keep_default=False)

        # Deleting field 'UserAPIKey.userID'
        db.delete_column('common_userapikey', 'userID')

        # Deleting field 'UserAPIKey.key'
        db.delete_column('common_userapikey', 'key')

        # Adding field 'UserAPIKey.keyID'
        db.add_column('common_userapikey', 'keyID', self.gf('django.db.models.fields.IntegerField')(default=0, primary_key=True), keep_default=False)

        # Adding field 'UserAPIKey.vCode'
        db.add_column('common_userapikey', 'vCode', self.gf('django.db.models.fields.CharField')(default="", max_length=255), keep_default=False)


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'APIKey.userID'
        raise RuntimeError("Cannot reverse this migration. 'APIKey.userID' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'APIKey.key'
        raise RuntimeError("Cannot reverse this migration. 'APIKey.key' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'APIKey.charID'
        raise RuntimeError("Cannot reverse this migration. 'APIKey.charID' and its values cannot be restored.")

        # Deleting field 'APIKey.keyID'
        db.delete_column('common_apikey', 'keyID')

        # Deleting field 'APIKey.characterID'
        db.delete_column('common_apikey', 'characterID')

        # Deleting field 'APIKey.vCode'
        db.delete_column('common_apikey', 'vCode')

        # User chose to not deal with backwards NULL issues for 'UserAPIKey.userID'
        raise RuntimeError("Cannot reverse this migration. 'UserAPIKey.userID' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'UserAPIKey.key'
        raise RuntimeError("Cannot reverse this migration. 'UserAPIKey.key' and its values cannot be restored.")

        # Deleting field 'UserAPIKey.keyID'
        db.delete_column('common_userapikey', 'keyID')

        # Deleting field 'UserAPIKey.vCode'
        db.delete_column('common_userapikey', 'vCode')


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
        'common.url': {
            'Meta': {'object_name': 'Url'},
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
