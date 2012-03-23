#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding field 'Asset.is_bpc'
        db.add_column('assets_asset', 'is_bpc', self.gf('django.db.models.fields.NullBooleanField')(default=None, null=True, blank=True), keep_default=False)


    def backwards(self, orm):

        # Deleting field 'Asset.is_bpc'
        db.delete_column('assets_asset', 'is_bpc')


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
            'typeID': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'volume': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'assets.assetdiff': {
            'Meta': {'object_name': 'AssetDiff'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 3, 15, 1, 16, 16, 306000)', 'db_index': 'True'}),
            'flag': ('django.db.models.fields.BigIntegerField', [], {}),
            'hangarID': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'new': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'solarSystemID': ('django.db.models.fields.BigIntegerField', [], {}),
            'stationID': ('django.db.models.fields.BigIntegerField', [], {}),
            'typeID': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'volume': ('django.db.models.fields.BigIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['assets']
