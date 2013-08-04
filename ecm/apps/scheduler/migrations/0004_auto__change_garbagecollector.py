#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'GarbageCollector'
        db.delete_table(u'scheduler_garbagecollector')
        # Adding model 'GarbageCollector'
        db.create_table(u'scheduler_garbagecollector', (
            ('model', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('min_entries_threshold', self.gf('django.db.models.fields.BigIntegerField')(default=10000)),
            ('max_age_threshold', self.gf('django.db.models.fields.BigIntegerField')()),
            ('age_units', self.gf('django.db.models.fields.BigIntegerField')(default=18144000)),
        ))
        db.send_create_signal(u'scheduler', ['GarbageCollector'])

    def backwards(self, orm):
        # Deleting model 'GarbageCollector'
        db.delete_table(u'scheduler_garbagecollector')
        # Adding model 'GarbageCollector'
        db.create_table(u'scheduler_garbagecollector', (
            ('age_units', self.gf('django.db.models.fields.BigIntegerField')(default=18144000)),
            ('min_entries_threshold', self.gf('django.db.models.fields.BigIntegerField')(default=10000)),
            ('db_table', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('max_age_threshold', self.gf('django.db.models.fields.BigIntegerField')()),
        ))
        db.send_create_signal('scheduler', ['GarbageCollector'])


    models = {
        u'scheduler.scheduledtask': {
            'Meta': {'object_name': 'ScheduledTask'},
            'args': ('django.db.models.fields.CharField', [], {'default': "'{}'", 'max_length': '256'}),
            'frequency': ('django.db.models.fields.IntegerField', [], {}),
            'frequency_units': ('django.db.models.fields.IntegerField', [], {'default': '3600'}),
            'function': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_last_exec_success': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_one_shot': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_running': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_scheduled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_execution': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'next_execution': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['scheduler']