#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Timer'
        db.create_table('op_timer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.BigIntegerField')(default=21644)),
            ('timer', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('location_id', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('location', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('moon_id', self.gf('django.db.models.fields.BigIntegerField')(default=0, null=True, blank=True)),
            ('moon', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('cycle', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('friendly', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('owner_id', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
        ))
        db.send_create_signal('op', ['Timer'])


    def backwards(self, orm):
        # Deleting model 'Timer'
        db.delete_table('op_timer')


    models = {
        'op.timer': {
            'Meta': {'ordering': "['timer']", 'object_name': 'Timer'},
            'cycle': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'friendly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'location_id': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'moon': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'moon_id': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'owner_id': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'structure': ('django.db.models.fields.BigIntegerField', [], {'default': '21644'}),
            'timer': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['op']