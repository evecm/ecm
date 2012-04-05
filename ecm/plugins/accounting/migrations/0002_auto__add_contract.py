#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Contract'
        db.create_table('accounting_contract', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contractID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('issuerID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('issuerCorpID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('assigneeID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('acceptorID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('startStationID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('endStationID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('forCorp', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('availability', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('dateIssued', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('dateExpired', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('dateAccepted', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('numDays', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('dateCompleted', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('reward', self.gf('django.db.models.fields.FloatField')()),
            ('collateral', self.gf('django.db.models.fields.FloatField')()),
            ('buyout', self.gf('django.db.models.fields.FloatField')()),
            ('volume', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('accounting', ['Contract'])


    def backwards(self, orm):

        # Deleting model 'Contract'
        db.delete_table('accounting_contract')


    models = {
        'accounting.contract': {
            'Meta': {'ordering': "['contractID']", 'object_name': 'Contract'},
            'acceptorID': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'assigneeID': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'availability': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'buyout': ('django.db.models.fields.FloatField', [], {}),
            'collateral': ('django.db.models.fields.FloatField', [], {}),
            'contractID': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'dateAccepted': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'dateCompleted': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'dateExpired': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'dateIssued': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'endStationID': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'forCorp': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issuerCorpID': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'issuerID': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'numDays': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'reward': ('django.db.models.fields.FloatField', [], {}),
            'startStationID': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'volume': ('django.db.models.fields.FloatField', [], {})
        },
        'accounting.entrytype': {
            'Meta': {'object_name': 'EntryType'},
            'refTypeID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'refTypeName': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'accounting.journalentry': {
            'Meta': {'object_name': 'JournalEntry'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'argID1': ('django.db.models.fields.BigIntegerField', [], {}),
            'argName1': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'balance': ('django.db.models.fields.FloatField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'ownerID1': ('django.db.models.fields.BigIntegerField', [], {}),
            'ownerID2': ('django.db.models.fields.BigIntegerField', [], {}),
            'ownerName1': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'ownerName2': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'refID': ('django.db.models.fields.BigIntegerField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounting.EntryType']"}),
            'wallet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corp.Wallet']"})
        },
        'corp.wallet': {
            'Meta': {'ordering': "['walletID']", 'object_name': 'Wallet'},
            'accessLvl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'walletID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['accounting']
