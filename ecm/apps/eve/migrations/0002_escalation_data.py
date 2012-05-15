#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
import bz2
import shutil
import tempfile
import os
from ecm.admin.util import log
import urllib2

PATCHED_EVE_DB_URL = 'http://releases.eve-corp-management.org/eve/eve_ecm.json-5.bz2'

class Migration(DataMigration):

    def forwards(self, orm):
        try:
            tempdir = tempfile.mkdtemp()
            eve_fixture_archive = os.path.join(tempdir, 'eve_ecm.json.bz2')
            
            log('Downloading EVE database from %s to %s...', PATCHED_EVE_DB_URL, eve_fixture_archive)
            req = urllib2.urlopen(PATCHED_EVE_DB_URL)
            fp = open(eve_fixture_archive, 'wb')
            shutil.copyfileobj(req, fp)
            fp.close()
            req.close()
            log('Download complete.')
    
            eve_fixture = os.path.join(tempdir, 'eve_data.json')
            
            log('Expanding %s to %s...', eve_fixture_archive, eve_fixture)
            bz2_file_desc = bz2.BZ2File(eve_fixture_archive, 'rb')
            json_file_desc = open(eve_fixture, 'wb')
            
            shutil.copyfileobj(bz2_file_desc, json_file_desc)
            
            bz2_file_desc.close()
            json_file_desc.close()
            log('Expansion complete.')
            
            log('Importing EVE data from %s...' % eve_fixture)
            from django.core.management import call_command
            call_command("loaddata", eve_fixture, commit=False)
            
        finally:
            log('Removing temp files...')
            shutil.rmtree(tempdir)
            log('done')
        

    def backwards(self, orm):
        pass


    models = {
        'eve.blueprintreq': {
            'Meta': {'ordering': "['blueprint', 'activityID', 'required_type']", 'unique_together': "(('blueprint', 'activityID', 'required_type'),)", 'object_name': 'BlueprintReq'},
            'activityID': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'baseMaterial': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'blueprint': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'requirements'", 'primary_key': 'True', 'db_column': "'blueprintTypeID'", 'to': "orm['eve.BlueprintType']"}),
            'damagePerJob': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
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
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.Group']", 'db_column': "'groupID'"}),
            'itemID': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'itemName': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'regionID': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'security': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'solarSystemID': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve.Type']", 'db_column': "'typeID'"}),
            'x': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'y': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'z': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'eve.controltowerresource': {
            'Meta': {'ordering': "['control_tower', 'resource']", 'unique_together': "(('control_tower', 'resource'),)", 'object_name': 'ControlTowerResource'},
            'control_tower': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tower_resources_t'", 'primary_key': 'True', 'db_column': "'controlTowerTypeID'", 'to': "orm['eve.Type']"}),
            'factionID': ('django.db.models.fields.SmallIntegerField', [], {}),
            'minSecurityLevel': ('django.db.models.fields.FloatField', [], {}),
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
            'iconID': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
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

    complete_apps = ['eve']
    symmetrical = True
