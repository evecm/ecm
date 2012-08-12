#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_column('assets_asset', 'typeID', 'eve_type_id')
        db.rename_column('assets_assetdiff', 'typeID', 'eve_type_id')
        
        db.alter_column('assets_asset', 'eve_type_id',
                        self.gf('ecm.lib.softfk.SoftForeignKey')(to=orm['eve.Type'], null=True))
        db.alter_column('assets_assetdiff', 'eve_type_id',
                        self.gf('ecm.lib.softfk.SoftForeignKey')(to=orm['eve.Type'], null=True))

    def backwards(self, orm):
        db.alter_column('assets_asset', 'typeID',
                        self.gf('django.db.models.fields.PositiveIntegerField')(default=0))
        db.alter_column('assets_assetdiff', 'typeID',
                        self.gf('django.db.models.fields.PositiveIntegerField')(default=0))

        db.rename_column('assets_asset', 'eve_type_id', 'typeID')
        db.rename_column('assets_assetdiff', 'eve_type_id', 'typeID')

    models = {
        'assets.asset': {
            'Meta': {'object_name': 'Asset'},
            'closest_object_id': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'container1': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'container2': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'flag': ('django.db.models.fields.BigIntegerField', [], {}),
            'hangarID': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'hasContents': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_bpc': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'itemID': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'quantity': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'singleton': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'solarSystemID': ('django.db.models.fields.BigIntegerField', [], {}),
            'stationID': ('django.db.models.fields.BigIntegerField', [], {}),
            'type': ('ecm.lib.softfk.SoftForeignKey', [], {'to': "orm['eve.Type']", 'null': 'True'}),
            'volume': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'assets.assetdiff': {
            'Meta': {'object_name': 'AssetDiff'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 6, 6, 0, 0)', 'db_index': 'True'}),
            'flag': ('django.db.models.fields.BigIntegerField', [], {}),
            'hangarID': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'new': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'solarSystemID': ('django.db.models.fields.BigIntegerField', [], {}),
            'stationID': ('django.db.models.fields.BigIntegerField', [], {}),
            'typeID': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'volume': ('django.db.models.fields.BigIntegerField', [], {'default': '0'})
        },
        'eve.blueprinttype': {
            'Meta': {'ordering': "['blueprintTypeID']", 'object_name': 'BlueprintType'},
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
            'Meta': {'ordering': "['categoryID']", 'object_name': 'Category'},
            'categoryID': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'categoryName': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'iconID': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.SmallIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
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
            'techLevel': ('django.db.models.fields.SmallIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'typeID': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'typeName': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'volume': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['assets']