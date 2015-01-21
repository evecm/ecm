# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'BlueprintType.data_interface'
        db.delete_column(u'eve_blueprinttype', 'dataInterfaceID')

        # Adding field 'BlueprintType.inventionBaseChance'
        db.add_column(u'eve_blueprinttype', 'inventionBaseChance',
                      self.gf('django.db.models.fields.FloatField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Type.techLevel'
        db.delete_column(u'eve_type', 'techLevel')


    def backwards(self, orm):
        # Adding field 'BlueprintType.data_interface'
        db.add_column(u'eve_blueprinttype', 'data_interface',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='blueprint_datainterfaces', null=True, to=orm['eve.Type'], db_column='dataInterfaceID', blank=True),
                      keep_default=False)

        # Deleting field 'BlueprintType.inventionBaseChance'
        db.delete_column(u'eve_blueprinttype', 'inventionBaseChance')

        # Adding field 'Type.techLevel'
        db.add_column(u'eve_type', 'techLevel',
                      self.gf('django.db.models.fields.SmallIntegerField')(blank=True, null=True, db_index=True),
                      keep_default=False)


    models = {
        'eve.blueprintreq': {
            'Meta': {'ordering': "['blueprint', 'activityID', 'required_type']", 'object_name': 'BlueprintReq'},
            'activityID': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'blueprint': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'requirements'", 'db_column': "'blueprintTypeID'", 'to': "orm['eve.BlueprintType']"}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'required_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.Type']", 'db_column': "'requiredTypeID'"})
        },
        'eve.blueprinttype': {
            'Meta': {'ordering': "['blueprintTypeID']", 'object_name': 'BlueprintType'},
            'blueprintTypeID': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'inventionBaseChance': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'inventionTime': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'maxProductionLimit': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent_blueprint': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children_blueprints'", 'null': 'True', 'db_column': "'parentBlueprintTypeID'", 'to': "orm['eve.BlueprintType']"}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['eve.Type']", 'unique': 'True', 'null': 'True', 'db_column': "'productTypeID'", 'blank': 'True'}),
            'productionTime': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'researchCopyTime': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'researchMaterialTime': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'researchProductivityTime': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'eve.category': {
            'Meta': {'ordering': "['categoryID']", 'object_name': 'Category'},
            'categoryID': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'categoryName': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'iconID': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.SmallIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'eve.celestialobject': {
            'Meta': {'ordering': "['itemID']", 'object_name': 'CelestialObject'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.Group']", 'null': 'True', 'db_column': "'groupID'", 'blank': 'True'}),
            'itemID': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'itemName': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'regionID': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'security': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'solarSystemID': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.Type']", 'db_column': "'typeID'"}),
            'x': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'y': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'z': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'eve.controltowerresource': {
            'Meta': {'ordering': "['control_tower', 'resource']", 'unique_together': "(('control_tower', 'resource'),)", 'object_name': 'ControlTowerResource'},
            'control_tower': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tower_resources_t'", 'db_column': "'controlTowerTypeID'", 'to': "orm['eve.Type']"}),
            'factionID': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'minSecurityLevel': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'purpose': ('django.db.models.fields.SmallIntegerField', [], {}),
            'quantity': ('django.db.models.fields.SmallIntegerField', [], {}),
            'resource': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tower_resources_r'", 'db_column': "'resourceTypeID'", 'to': "orm['eve.Type']"})
        },
        'eve.group': {
            'Meta': {'ordering': "['groupID']", 'object_name': 'Group'},
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
            'Meta': {'ordering': "['marketGroupID']", 'object_name': 'MarketGroup'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hasTypes': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'iconID': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'marketGroupID': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'marketGroupName': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parent_group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children_groups'", 'null': 'True', 'db_column': "'parentGroupID'", 'to': "orm['eve.MarketGroup']"})
        },
        'eve.skillreq': {
            'Meta': {'ordering': "['item', 'skill']", 'object_name': 'SkillReq'},
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'skill_reqs'", 'to': "orm['eve.Type']"}),
            'required_level': ('django.db.models.fields.SmallIntegerField', [], {}),
            'skill': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['eve.Type']"})
        },
        'eve.type': {
            'Meta': {'ordering': "['typeID']", 'object_name': 'Type'},
            'basePrice': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'blueprint': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['eve.BlueprintType']", 'unique': 'True', 'null': 'True', 'db_column': "'blueprintTypeID'", 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'types'", 'db_column': "'categoryID'", 'to': "orm['eve.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'types'", 'db_column': "'groupID'", 'to': "orm['eve.Group']"}),
            'market_group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'items'", 'null': 'True', 'db_column': "'marketGroupID'", 'to': "orm['eve.MarketGroup']"}),
            'metaGroupID': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'portionSize': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.SmallIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'raceID': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'typeID': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'typeName': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'volume': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['eve']