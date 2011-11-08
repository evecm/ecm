#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding field 'Corp.killboardUrl'
        db.add_column('corp_corp', 'killboardUrl', self.gf('django.db.models.fields.URLField')(max_length=255, null=True), keep_default=False)


    def backwards(self, orm):

        # Deleting field 'Corp.killboardUrl'
        db.delete_column('corp_corp', 'killboardUrl')


    models = {
        'corp.corp': {
            'Meta': {'ordering': "['id']", 'object_name': 'Corp'},
            'allianceID': ('django.db.models.fields.BigIntegerField', [], {}),
            'allianceName': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'allianceTicker': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'ceoID': ('django.db.models.fields.BigIntegerField', [], {}),
            'ceoName': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'corporationID': ('django.db.models.fields.BigIntegerField', [], {}),
            'corporationName': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'killboardUrl': ('django.db.models.fields.URLField', [], {'max_length': '255', 'null': 'True'}),
            'memberLimit': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'stationID': ('django.db.models.fields.BigIntegerField', [], {}),
            'stationName': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'taxRate': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'ticker': ('django.db.models.fields.CharField', [], {'max_length': '8'})
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
        }
    }

    complete_apps = ['corp']
