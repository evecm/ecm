#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.execute('DELETE FROM accounting_contractitem;')
        db.execute('DELETE FROM accounting_contract;')
        db.execute('DELETE FROM accounting_marketorder;')
        
        # Deleting model 'ContractItem'
        db.delete_table('accounting_contractitem')

        # Deleting model 'Contract'
        db.delete_table('accounting_contract')

        # Deleting model 'MarketOrder'
        db.delete_table('accounting_marketorder')

    def backwards(self, orm):
        # Adding model 'Contract'
        db.create_table('accounting_contract', (
            ('startStationID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('dateCompleted', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('assigneeID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('issuerID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('dateExpired', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('forCorp', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('availability', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('dateAccepted', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('dateIssued', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('issuerCorpID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('collateral', self.gf('django.db.models.fields.FloatField')()),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('volume', self.gf('django.db.models.fields.FloatField')()),
            ('endStationID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('buyout', self.gf('django.db.models.fields.FloatField')()),
            ('numDays', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('acceptorID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('reward', self.gf('django.db.models.fields.FloatField')()),
            ('contractID', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('accounting', ['Contract'])

        # Adding model 'ContractItem'
        db.create_table('accounting_contractitem', (
            ('recordID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('singleton', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('rawQuantity', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('typeID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('included', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contract', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounting.Contract'])),
            ('quantity', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('accounting', ['ContractItem'])

        # Adding model 'MarketOrder'
        db.create_table('accounting_marketorder', (
            ('orderID', self.gf('django.db.models.fields.PositiveIntegerField')(primary_key=True)),
            ('typeID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('volEntered', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('minVolume', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('accountKey', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('issued', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('bid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('stationID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('escrow', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('range', self.gf('django.db.models.fields.IntegerField')()),
            ('orderState', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('volRemaining', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('duration', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('charID', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('accounting', ['MarketOrder'])


    models = {
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