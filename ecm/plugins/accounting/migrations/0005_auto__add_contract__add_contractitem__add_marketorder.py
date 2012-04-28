#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Contract'
        db.create_table('accounting_contract', (
            ('contractID', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('issuerID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('issuerCorpID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('assigneeID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('acceptorID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('startStationID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('endStationID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('type', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('forCorp', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('availability', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('dateIssued', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('dateExpired', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('dateAccepted', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('dateCompleted', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('numDays', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('reward', self.gf('django.db.models.fields.FloatField')()),
            ('collateral', self.gf('django.db.models.fields.FloatField')()),
            ('buyout', self.gf('django.db.models.fields.FloatField')()),
            ('volume', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('accounting', ['Contract'])

        # Adding model 'ContractItem'
        db.create_table('accounting_contractitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contract', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['accounting.Contract'])),
            ('recordID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('typeID', self.gf('django.db.models.fields.IntegerField')()),
            ('quantity', self.gf('django.db.models.fields.BigIntegerField')()),
            ('rawQuantity', self.gf('django.db.models.fields.BigIntegerField')()),
            ('singleton', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('included', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal('accounting', ['ContractItem'])

        # Adding model 'MarketOrder'
        db.create_table('accounting_marketorder', (
            ('orderID', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('charID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('stationID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('volEntered', self.gf('django.db.models.fields.BigIntegerField')()),
            ('volRemaining', self.gf('django.db.models.fields.BigIntegerField')()),
            ('minVolume', self.gf('django.db.models.fields.BigIntegerField')()),
            ('orderState', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('typeID', self.gf('django.db.models.fields.IntegerField')()),
            ('range', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('accountKey', self.gf('django.db.models.fields.related.ForeignKey')(related_name='market_orders', to=orm['corp.Wallet'])),
            ('duration', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('escrow', self.gf('django.db.models.fields.FloatField')()),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('bid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('issued', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('accounting', ['MarketOrder'])

    def backwards(self, orm):
        # Deleting model 'Contract'
        db.delete_table('accounting_contract')

        # Deleting model 'ContractItem'
        db.delete_table('accounting_contractitem')

        # Deleting model 'MarketOrder'
        db.delete_table('accounting_marketorder')

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
        'corp.wallet': {
            'Meta': {'ordering': "['walletID']", 'object_name': 'Wallet'},
            'accessLvl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'walletID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['accounting']