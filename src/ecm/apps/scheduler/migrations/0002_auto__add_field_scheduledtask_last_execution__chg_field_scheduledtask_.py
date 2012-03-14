#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'ScheduledTask.last_execution'
        db.add_column('scheduler_scheduledtask', 'last_execution', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True), keep_default=False)

        # Changing field 'ScheduledTask.next_execution'
        db.alter_column('scheduler_scheduledtask', 'next_execution', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))


    def backwards(self, orm):
        
        # Deleting field 'ScheduledTask.last_execution'
        db.delete_column('scheduler_scheduledtask', 'last_execution')

        # Changing field 'ScheduledTask.next_execution'
        db.alter_column('scheduler_scheduledtask', 'next_execution', self.gf('django.db.models.fields.DateTimeField')())


    models = {
        'scheduler.garbagecollector': {
            'Meta': {'object_name': 'GarbageCollector'},
            'age_units': ('django.db.models.fields.BigIntegerField', [], {'default': '18144000'}),
            'db_table': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'max_age_threshold': ('django.db.models.fields.BigIntegerField', [], {}),
            'min_entries_threshold': ('django.db.models.fields.BigIntegerField', [], {'default': '10000'})
        },
        'scheduler.scheduledtask': {
            'Meta': {'ordering': "('-priority', 'function')", 'object_name': 'ScheduledTask'},
            'args': ('django.db.models.fields.CharField', [], {'default': "'{}'", 'max_length': '256'}),
            'frequency': ('django.db.models.fields.IntegerField', [], {}),
            'frequency_units': ('django.db.models.fields.IntegerField', [], {'default': '3600'}),
            'function': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_last_exec_success': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_one_shot': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_running': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_execution': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'next_execution': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['scheduler']
