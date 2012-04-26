# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Contract.id'
        db.delete_column('accounting_contract', 'id')


        # Changing field 'Contract.contractID'
        db.alter_column('accounting_contract', 'contractID', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True))

        # Changing field 'ContractItem.contract'
        db.alter_column('accounting_contractitem', 'contract_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounting.Contract']))
    def backwards(self, orm):
        # Adding field 'Contract.id'
        db.add_column('accounting_contract', 'id',
                      self.gf('django.db.models.fields.AutoField')(default=0, primary_key=True),
                      keep_default=False)


        # Changing field 'Contract.contractID'
        db.alter_column('accounting_contract', 'contractID', self.gf('django.db.models.fields.BigIntegerField')(unique=True))

        # Changing field 'ContractItem.contract'
        db.alter_column('accounting_contractitem', 'contract_id', self.gf('django.db.models.fields.related.ForeignKey')(to_field='contractID', to=orm['accounting.Contract']))
    models = {
        'accounting.contract': {
            'Meta': {'ordering': "['contractID']", 'object_name': 'Contract'},
            'acceptorID': ('django.db.models.fields.BigIntegerField', [], {}),
            'assigneeID': ('django.db.models.fields.BigIntegerField', [], {}),
            'availability': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'buyout': ('django.db.models.fields.FloatField', [], {}),
            'collateral': ('django.db.models.fields.FloatField', [], {}),
            'contractID': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'dateAccepted': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'dateCompleted': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'dateExpired': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'dateIssued': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'endStationID': ('django.db.models.fields.BigIntegerField', [], {}),
            'forCorp': ('django.db.models.fields.BigIntegerField', [], {}),
            'issuerCorpID': ('django.db.models.fields.BigIntegerField', [], {}),
            'issuerID': ('django.db.models.fields.BigIntegerField', [], {}),
            'numDays': ('django.db.models.fields.BigIntegerField', [], {}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'reward': ('django.db.models.fields.FloatField', [], {}),
            'startStationID': ('django.db.models.fields.BigIntegerField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'volume': ('django.db.models.fields.FloatField', [], {})
        },
        'accounting.contractitem': {
            'Meta': {'object_name': 'ContractItem'},
            'contract': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['accounting.Contract']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'included': ('django.db.models.fields.BigIntegerField', [], {}),
            'quantity': ('django.db.models.fields.BigIntegerField', [], {}),
            'rawQuantity': ('django.db.models.fields.BigIntegerField', [], {}),
            'recordID': ('django.db.models.fields.BigIntegerField', [], {}),
            'singleton': ('django.db.models.fields.BigIntegerField', [], {}),
            'typeID': ('django.db.models.fields.BigIntegerField', [], {})
        },
        'accounting.entrytype': {
            'Meta': {'object_name': 'EntryType'},
            'refTypeID': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
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
            'accountKey': ('django.db.models.fields.BigIntegerField', [], {}),
            'bid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'charID': ('django.db.models.fields.BigIntegerField', [], {}),
            'duration': ('django.db.models.fields.BigIntegerField', [], {}),
            'escrow': ('django.db.models.fields.BigIntegerField', [], {}),
            'issued': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'minVolume': ('django.db.models.fields.BigIntegerField', [], {}),
            'orderID': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'orderState': ('django.db.models.fields.BigIntegerField', [], {}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'range': ('django.db.models.fields.BigIntegerField', [], {}),
            'stationID': ('django.db.models.fields.BigIntegerField', [], {}),
            'typeID': ('django.db.models.fields.BigIntegerField', [], {}),
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