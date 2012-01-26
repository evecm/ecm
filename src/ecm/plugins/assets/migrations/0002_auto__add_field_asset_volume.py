#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding field 'Asset.volume'
        db.add_column('assets_asset', 'volume', self.gf('django.db.models.fields.FloatField')(default=0.0), keep_default=False)


    def backwards(self, orm):

        # Deleting field 'Asset.volume'
        db.delete_column('assets_asset', 'volume')


    models = {
        'assets.asset': {
            'Meta': {'object_name': 'Asset'},
            'container1': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'container2': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'flag': ('django.db.models.fields.BigIntegerField', [], {}),
            'hangarID': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'hasContents': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'itemID': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'singleton': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'solarSystemID': ('django.db.models.fields.BigIntegerField', [], {}),
            'stationID': ('django.db.models.fields.BigIntegerField', [], {}),
            'typeID': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'volume': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'assets.assetdiff': {
            'Meta': {'object_name': 'AssetDiff'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 18, 20, 45, 0, 448000)', 'db_index': 'True'}),
            'flag': ('django.db.models.fields.BigIntegerField', [], {}),
            'hangarID': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'new': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'solarSystemID': ('django.db.models.fields.BigIntegerField', [], {}),
            'stationID': ('django.db.models.fields.BigIntegerField', [], {}),
            'typeID': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['assets']
