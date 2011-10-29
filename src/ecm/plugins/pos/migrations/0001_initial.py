# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'POS'
        db.create_table('pos_pos', (
            ('itemID', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('locationID', self.gf('django.db.models.fields.BigIntegerField')(db_index=True)),
            ('location', self.gf('django.db.models.fields.CharField')(default='???', max_length=256)),
            ('moonID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('mlocation', self.gf('django.db.models.fields.CharField')(default='???', max_length=256)),
            ('typeID', self.gf('django.db.models.fields.IntegerField')()),
            ('state', self.gf('django.db.models.fields.IntegerField')()),
            ('stateTimestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('onlineTimestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('cachedUntil', self.gf('django.db.models.fields.DateTimeField')()),
            ('standingOwnerID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('typeName', self.gf('django.db.models.fields.CharField')(default='???', max_length=256)),
            ('usageFlags', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('deployFlags', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('onStandingDropStanding', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('allowCorporationMembers', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allowAllianceMembers', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('onStatusDropEnabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('onStatusDropStanding', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('onAggressionEnabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('onCorporationWarEnabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('customName', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('lastUpdate', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('pos', ['POS'])

        # Adding M2M table for field operators on 'POS'
        db.create_table('pos_pos_operators', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pos', models.ForeignKey(orm['pos.pos'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('pos_pos_operators', ['pos_id', 'user_id'])

        # Adding model 'FuelLevel'
        db.create_table('pos_fuellevel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pos', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fuel_levels', to=orm['pos.POS'])),
            ('typeID', self.gf('django.db.models.fields.IntegerField')()),
            ('quantity', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
        ))
        db.send_create_signal('pos', ['FuelLevel'])


    def backwards(self, orm):
        
        # Deleting model 'POS'
        db.delete_table('pos_pos')

        # Removing M2M table for field operators on 'POS'
        db.delete_table('pos_pos_operators')

        # Deleting model 'FuelLevel'
        db.delete_table('pos_fuellevel')


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
        'pos.fuellevel': {
            'Meta': {'ordering': "['pos', 'typeID', 'date']", 'object_name': 'FuelLevel'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pos': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fuel_levels'", 'to': "orm['pos.POS']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {}),
            'typeID': ('django.db.models.fields.IntegerField', [], {})
        },
        'pos.pos': {
            'Meta': {'object_name': 'POS'},
            'allowAllianceMembers': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allowCorporationMembers': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cachedUntil': ('django.db.models.fields.DateTimeField', [], {}),
            'customName': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'deployFlags': ('django.db.models.fields.SmallIntegerField', [], {}),
            'itemID': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'lastUpdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "'???'", 'max_length': '256'}),
            'locationID': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'mlocation': ('django.db.models.fields.CharField', [], {'default': "'???'", 'max_length': '256'}),
            'moonID': ('django.db.models.fields.BigIntegerField', [], {}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'onAggressionEnabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'onCorporationWarEnabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'onStandingDropStanding': ('django.db.models.fields.SmallIntegerField', [], {}),
            'onStatusDropEnabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'onStatusDropStanding': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'onlineTimestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'operators': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'operated_poses'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'standingOwnerID': ('django.db.models.fields.BigIntegerField', [], {}),
            'state': ('django.db.models.fields.IntegerField', [], {}),
            'stateTimestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'typeID': ('django.db.models.fields.IntegerField', [], {}),
            'typeName': ('django.db.models.fields.CharField', [], {'default': "'???'", 'max_length': '256'}),
            'usageFlags': ('django.db.models.fields.SmallIntegerField', [], {})
        }
    }

    complete_apps = ['pos']
