#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'TransactionEntry'
        db.create_table('accounting_transactionentry', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('quantity', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('typeID', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('price', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('clientID', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('clientName', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('stationID', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('transactionType', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('transactionFor', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('journal', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='JournalEntry', null=True, to=orm['accounting.JournalEntry'])),
            ('wallet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['corp.Wallet'])),
        ))
        db.send_create_signal('accounting', ['TransactionEntry'])


    def backwards(self, orm):
        
        # Deleting model 'TransactionEntry'
        db.delete_table('accounting_transactionentry')


    models = {
        'accounting.contract': {
            'Meta': {'ordering': "['contractID']", 'object_name': 'Contract'},
            'acceptorID': ('django.db.models.fields.BigIntegerField', [], {}),
            'assigneeID': ('django.db.models.fields.BigIntegerField', [], {}),
            'availability': ('django.db.models.fields.SmallIntegerField', [], {}),
            'buyout': ('django.db.models.fields.FloatField', [], {}),
            'collateral': ('django.db.models.fields.FloatField', [], {}),
            'contractID': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'dateAccepted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dateCompleted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dateExpired': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dateIssued': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'endStationID': ('django.db.models.fields.BigIntegerField', [], {}),
            'forCorp': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'issuerCorpID': ('django.db.models.fields.BigIntegerField', [], {}),
            'issuerID': ('django.db.models.fields.BigIntegerField', [], {}),
            'numDays': ('django.db.models.fields.SmallIntegerField', [], {}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'reward': ('django.db.models.fields.FloatField', [], {}),
            'startStationID': ('django.db.models.fields.BigIntegerField', [], {}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.SmallIntegerField', [], {}),
            'volume': ('django.db.models.fields.FloatField', [], {})
        },
        'accounting.contractitem': {
            'Meta': {'object_name': 'ContractItem'},
            'contract': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['accounting.Contract']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'included': ('django.db.models.fields.SmallIntegerField', [], {}),
            'quantity': ('django.db.models.fields.BigIntegerField', [], {}),
            'rawQuantity': ('django.db.models.fields.BigIntegerField', [], {}),
            'recordID': ('django.db.models.fields.BigIntegerField', [], {}),
            'singleton': ('django.db.models.fields.SmallIntegerField', [], {}),
            'typeID': ('django.db.models.fields.IntegerField', [], {})
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
        'accounting.marketorder': {
            'Meta': {'ordering': "['orderID']", 'object_name': 'MarketOrder'},
            'accountKey': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'market_orders'", 'to': "orm['corp.Wallet']"}),
            'bid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'charID': ('django.db.models.fields.BigIntegerField', [], {}),
            'duration': ('django.db.models.fields.SmallIntegerField', [], {}),
            'escrow': ('django.db.models.fields.FloatField', [], {}),
            'issued': ('django.db.models.fields.DateTimeField', [], {}),
            'minVolume': ('django.db.models.fields.BigIntegerField', [], {}),
            'orderID': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'orderState': ('django.db.models.fields.SmallIntegerField', [], {}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'range': ('django.db.models.fields.SmallIntegerField', [], {}),
            'stationID': ('django.db.models.fields.BigIntegerField', [], {}),
            'typeID': ('django.db.models.fields.IntegerField', [], {}),
            'volEntered': ('django.db.models.fields.BigIntegerField', [], {}),
            'volRemaining': ('django.db.models.fields.BigIntegerField', [], {})
        },
        'accounting.report': {
            'Meta': {'object_name': 'Report'},
            'default_period': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'default_step': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'entry_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['accounting.EntryType']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'accounting.transactionentry': {
            'Meta': {'ordering': "['date']", 'object_name': 'TransactionEntry'},
            'clientID': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'clientName': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'journal': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'JournalEntry'", 'null': 'True', 'to': "orm['accounting.JournalEntry']"}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'quantity': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stationID': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'transactionFor': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'transactionType': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'typeID': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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
