#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'POS'
        db.create_table('pos_pos', (
            ('itemID', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('locationID', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('location', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('moonID', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('moon', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('typeID', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('typeName', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('state', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('stateTimestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('onlineTimestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('cachedUntil', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('usageFlags', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('deployFlags', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('allowCorporationMembers', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allowAllianceMembers', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('useStandingsFrom', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('standingThreshold', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('securityStatusThreshold', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('attackOnConcordFlag', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('attackOnAggression', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('attackOnCorpWar', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('lastUpdate', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('isotopeTypeID', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('customName', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
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
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('typeID', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('quantity', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('pos', ['FuelLevel'])

        # Adding model 'FuelConsumption'
        db.create_table('pos_fuelconsumption', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pos', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fuel_consumptions', to=orm['pos.POS'])),
            ('typeID', self.gf('django.db.models.fields.IntegerField')()),
            ('consumption', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('stability', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('probableConsumption', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('probableStability', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('pos', ['FuelConsumption'])


    def backwards(self, orm):

        # Deleting model 'POS'
        db.delete_table('pos_pos')

        # Removing M2M table for field operators on 'POS'
        db.delete_table('pos_pos_operators')

        # Deleting model 'FuelLevel'
        db.delete_table('pos_fuellevel')

        # Deleting model 'FuelConsumption'
        db.delete_table('pos_fuelconsumption')


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
        'pos.fuelconsumption': {
            'Meta': {'ordering': "['pos', 'typeID']", 'object_name': 'FuelConsumption'},
            'consumption': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pos': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fuel_consumptions'", 'to': "orm['pos.POS']"}),
            'probableConsumption': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'probableStability': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'stability': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'typeID': ('django.db.models.fields.IntegerField', [], {})
        },
        'pos.fuellevel': {
            'Meta': {'ordering': "['pos', 'date', 'typeID']", 'object_name': 'FuelLevel'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pos': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fuel_levels'", 'to': "orm['pos.POS']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {}),
            'typeID': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        'pos.pos': {
            'Meta': {'object_name': 'POS'},
            'allowAllianceMembers': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allowCorporationMembers': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'attackOnAggression': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'attackOnConcordFlag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'attackOnCorpWar': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cachedUntil': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customName': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'deployFlags': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'isotopeTypeID': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'itemID': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'lastUpdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'locationID': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'moon': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'moonID': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'onlineTimestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'operators': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'operated_poses'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'securityStatusThreshold': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'standingThreshold': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'state': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'stateTimestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'typeID': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'typeName': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'usageFlags': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'useStandingsFrom': ('django.db.models.fields.BigIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['pos']
