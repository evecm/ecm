#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Report'
        db.create_table('accounting_report', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('default_period', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('default_step', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('accounting', ['Report'])

        # Adding M2M table for field entry_types on 'Report'
        db.create_table('accounting_report_entry_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('report', models.ForeignKey(orm['accounting.report'], null=False)),
            ('entrytype', models.ForeignKey(orm['accounting.entrytype'], null=False))
        ))
        db.create_unique('accounting_report_entry_types', ['report_id', 'entrytype_id'])

    def backwards(self, orm):
        # Deleting model 'Report'
        db.delete_table('accounting_report')

        # Removing M2M table for field entry_types on 'Report'
        db.delete_table('accounting_report_entry_types')

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
        'corp.wallet': {
            'Meta': {'ordering': "['walletID']", 'object_name': 'Wallet'},
            'accessLvl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'walletID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['accounting']