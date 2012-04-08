# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Renaming column for 'MarketOrder.typeID' to match new field type.
        db.rename_column('accounting_marketorder', 'typeID', 'typeID_id')
        # Changing field 'MarketOrder.typeID'
        db.alter_column('accounting_marketorder', 'typeID_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eve.Type']))

        # Adding index on 'MarketOrder', fields ['typeID']
        db.create_index('accounting_marketorder', ['typeID_id'])


    def backwards(self, orm):
        
        # Removing index on 'MarketOrder', fields ['typeID']
        db.delete_index('accounting_marketorder', ['typeID_id'])

        # Renaming column for 'MarketOrder.typeID' to match new field type.
        db.rename_column('accounting_marketorder', 'typeID_id', 'typeID')
        # Changing field 'MarketOrder.typeID'
        db.alter_column('accounting_marketorder', 'typeID', self.gf('django.db.models.fields.PositiveIntegerField')())


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
        'accounting.contractitem': {
            'Meta': {'ordering': "['recordID']", 'object_name': 'ContractItem'},
            'contract': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounting.Contract']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'included': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'rawQuantity': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'recordID': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'singleton': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'typeID': ('django.db.models.fields.PositiveIntegerField', [], {})
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
            'accountKey': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'bid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'charID': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'escrow': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'issued': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'minVolume': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'orderID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'orderState': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounting.OrderState']"}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'range': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'stationID': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'typeID': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.Type']"}),
            'volEntered': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'volRemaining': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'accounting.orderstate': {
            'Meta': {'ordering': "['description']", 'object_name': 'OrderState'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stateID': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'corp.wallet': {
            'Meta': {'ordering': "['walletID']", 'object_name': 'Wallet'},
            'accessLvl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'walletID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'})
        },
        'eve.blueprinttype': {
            'Meta': {'ordering': "['blueprintTypeID']", 'object_name': 'BlueprintType', 'db_table': "'invBlueprintTypes'", 'managed': 'False'},
            'blueprintTypeID': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'data_interface': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'blueprint_datainterfaces'", 'null': 'True', 'db_column': "'dataInterfaceID'", 'to': "orm['eve.Type']"}),
            'materialModifier': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'maxProductionLimit': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent_blueprint': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children_blueprints'", 'null': 'True', 'db_column': "'parentBlueprintTypeID'", 'to': "orm['eve.BlueprintType']"}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['eve.Type']", 'unique': 'True', 'null': 'True', 'db_column': "'productTypeID'", 'blank': 'True'}),
            'productionTime': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'productivityModifier': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'researchCopyTime': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'researchMaterialTime': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'researchProductivityTime': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'researchTechTime': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'techLevel': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'wasteFactor': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'eve.category': {
            'Meta': {'ordering': "['categoryID']", 'object_name': 'Category', 'db_table': "'invCategories'", 'managed': 'False'},
            'categoryID': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'categoryName': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'iconID': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.SmallIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'eve.group': {
            'Meta': {'ordering': "['groupID']", 'object_name': 'Group', 'db_table': "'invGroups'", 'managed': 'False'},
            'allowManufacture': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'allowRecycler': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'anchorable': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'anchored': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groups'", 'db_column': "'categoryID'", 'to': "orm['eve.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fittableNonSingleton': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'groupID': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'groupName': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'iconID': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'useBasePrice': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'eve.marketgroup': {
            'Meta': {'ordering': "['marketGroupID']", 'object_name': 'MarketGroup', 'db_table': "'invMarketGroups'", 'managed': 'False'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hasTypes': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'iconID': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'marketGroupID': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'marketGroupName': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parent_group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children_groups'", 'null': 'True', 'db_column': "'parentGroupID'", 'to': "orm['eve.MarketGroup']"})
        },
        'eve.type': {
            'Meta': {'ordering': "['typeID']", 'object_name': 'Type', 'db_table': "'invTypes'", 'managed': 'False'},
            'basePrice': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'blueprint': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['eve.BlueprintType']", 'unique': 'True', 'null': 'True', 'db_column': "'blueprintTypeID'", 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'types'", 'db_column': "'categoryID'", 'to': "orm['eve.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'types'", 'db_column': "'groupID'", 'to': "orm['eve.Group']"}),
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'market_group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'items'", 'null': 'True', 'db_column': "'marketGroupID'", 'to': "orm['eve.MarketGroup']"}),
            'metaGroupID': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'portionSize': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.SmallIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'raceID': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'techLevel': ('django.db.models.fields.SmallIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'typeID': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'typeName': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'volume': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['accounting']
