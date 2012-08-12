#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Category'
        db.create_table('eve_category', (
            ('categoryID', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('categoryName', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('iconID', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('published', self.gf('django.db.models.fields.SmallIntegerField')(db_index=True, null=True, blank=True)),
        ))
        db.send_create_signal('eve', ['Category'])

        # Adding model 'Group'
        db.create_table('eve_group', (
            ('groupID', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='groups', db_column='categoryID', to=orm['eve.Category'])),
            ('groupName', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('iconID', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('useBasePrice', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('allowManufacture', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('allowRecycler', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('anchored', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('anchorable', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('fittableNonSingleton', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('published', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('eve', ['Group'])

        # Adding model 'ControlTowerResource'
        db.create_table('eve_controltowerresource', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('control_tower', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tower_resources_t', db_column='controlTowerTypeID', to=orm['eve.Type'])),
            ('resource', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tower_resources_r', db_column='resourceTypeID', to=orm['eve.Type'])),
            ('purpose', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('quantity', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('minSecurityLevel', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('factionID', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('eve', ['ControlTowerResource'])

        # Adding unique constraint on 'ControlTowerResource', fields ['control_tower', 'resource']
        db.create_unique('eve_controltowerresource', ['controlTowerTypeID', 'resourceTypeID'])

        # Adding model 'MarketGroup'
        db.create_table('eve_marketgroup', (
            ('marketGroupID', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('parent_group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children_groups', null=True, db_column='parentGroupID', to=orm['eve.MarketGroup'])),
            ('marketGroupName', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('iconID', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('hasTypes', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('eve', ['MarketGroup'])

        # Adding model 'BlueprintType'
        db.create_table('eve_blueprinttype', (
            ('blueprintTypeID', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('parent_blueprint', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children_blueprints', null=True, db_column='parentBlueprintTypeID', to=orm['eve.BlueprintType'])),
            ('product', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['eve.Type'], unique=True, null=True, db_column='productTypeID', blank=True)),
            ('productionTime', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('techLevel', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('data_interface', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='blueprint_datainterfaces', null=True, db_column='dataInterfaceID', to=orm['eve.Type'])),
            ('researchProductivityTime', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('researchMaterialTime', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('researchCopyTime', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('researchTechTime', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('productivityModifier', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('materialModifier', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('wasteFactor', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('maxProductionLimit', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('eve', ['BlueprintType'])

        # Adding model 'BlueprintReq'
        db.create_table('eve_blueprintreq', (
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('blueprint', self.gf('django.db.models.fields.related.ForeignKey')(related_name='requirements', db_column='blueprintTypeID', to=orm['eve.BlueprintType'])),
            ('activityID', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('required_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eve.Type'], db_column='requiredTypeID')),
            ('quantity', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('damagePerJob', self.gf('django.db.models.fields.FloatField')(default=1.0)),
            ('baseMaterial', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('eve', ['BlueprintReq'])

        # Adding model 'Type'
        db.create_table('eve_type', (
            ('typeID', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='types', db_column='groupID', to=orm['eve.Group'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='types', db_column='categoryID', to=orm['eve.Category'])),
            ('typeName', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('blueprint', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['eve.BlueprintType'], unique=True, null=True, db_column='blueprintTypeID', blank=True)),
            ('techLevel', self.gf('django.db.models.fields.SmallIntegerField')(db_index=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('volume', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('portionSize', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('raceID', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('basePrice', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('market_group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='items', null=True, db_column='marketGroupID', to=orm['eve.MarketGroup'])),
            ('metaGroupID', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('published', self.gf('django.db.models.fields.SmallIntegerField')(db_index=True, null=True, blank=True)),
        ))
        db.send_create_signal('eve', ['Type'])

        # Adding model 'CelestialObject'
        db.create_table('eve_celestialobject', (
            ('itemID', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eve.Type'], db_column='typeID')),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eve.Group'], null=True, db_column='groupID', blank=True)),
            ('solarSystemID', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('regionID', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('itemName', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('security', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('x', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('y', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('z', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('eve', ['CelestialObject'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'ControlTowerResource', fields ['control_tower', 'resource']
        db.delete_unique('eve_controltowerresource', ['controlTowerTypeID', 'resourceTypeID'])

        # Deleting model 'Category'
        db.delete_table('eve_category')

        # Deleting model 'Group'
        db.delete_table('eve_group')

        # Deleting model 'ControlTowerResource'
        db.delete_table('eve_controltowerresource')

        # Deleting model 'MarketGroup'
        db.delete_table('eve_marketgroup')

        # Deleting model 'BlueprintType'
        db.delete_table('eve_blueprinttype')

        # Deleting model 'BlueprintReq'
        db.delete_table('eve_blueprintreq')

        # Deleting model 'Type'
        db.delete_table('eve_type')

        # Deleting model 'CelestialObject'
        db.delete_table('eve_celestialobject')


    models = {
        'eve.blueprintreq': {
            'Meta': {'ordering': "['blueprint', 'activityID', 'required_type']", 'object_name': 'BlueprintReq'},
            'activityID': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'baseMaterial': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'blueprint': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'requirements'", 'db_column': "'blueprintTypeID'", 'to': "orm['eve.BlueprintType']"}),
            'damagePerJob': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'required_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.Type']", 'db_column': "'requiredTypeID'"})
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

    complete_apps = ['eve']
