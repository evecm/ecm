#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Timer.moon'
        db.delete_column('op_timer', 'moon')

        # Deleting field 'Timer.moon_id'
        db.delete_column('op_timer', 'moon_id')

        # Adding field 'Timer.owner'
        db.add_column('op_timer', 'owner',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Timer.moon'
        db.add_column('op_timer', 'moon',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Timer.moon_id'
        db.add_column('op_timer', 'moon_id',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Timer.owner'
        db.delete_column('op_timer', 'owner')


    models = {
        'op.timer': {
            'Meta': {'ordering': "['timer']", 'object_name': 'Timer'},
            'cycle': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'friendly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'location_id': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'owner_id': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'structure': ('django.db.models.fields.BigIntegerField', [], {'default': '21644'}),
            'timer': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['op']