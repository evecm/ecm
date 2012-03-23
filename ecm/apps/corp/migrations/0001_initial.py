#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Hangar'
        db.create_table('corp_hangar', (
            ('hangarID', self.gf('django.db.models.fields.PositiveIntegerField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('accessLvl', self.gf('django.db.models.fields.PositiveIntegerField')(default=1000)),
        ))
        db.send_create_signal('corp', ['Hangar'])

        # Adding model 'Wallet'
        db.create_table('corp_wallet', (
            ('walletID', self.gf('django.db.models.fields.PositiveIntegerField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('accessLvl', self.gf('django.db.models.fields.PositiveIntegerField')(default=1000)),
        ))
        db.send_create_signal('corp', ['Wallet'])

        # Adding model 'Corp'
        db.create_table('corp_corp', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('corporationID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('corporationName', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('ticker', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('ceoID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('ceoName', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('stationID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('stationName', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('allianceID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('allianceName', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('allianceTicker', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('taxRate', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('memberLimit', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('corp', ['Corp'])


    def backwards(self, orm):
        
        # Deleting model 'Hangar'
        db.delete_table('corp_hangar')

        # Deleting model 'Wallet'
        db.delete_table('corp_wallet')

        # Deleting model 'Corp'
        db.delete_table('corp_corp')


    models = {
        'corp.corp': {
            'Meta': {'object_name': 'Corp'},
            'allianceID': ('django.db.models.fields.BigIntegerField', [], {}),
            'allianceName': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'allianceTicker': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'ceoID': ('django.db.models.fields.BigIntegerField', [], {}),
            'ceoName': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'corporationID': ('django.db.models.fields.BigIntegerField', [], {}),
            'corporationName': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
