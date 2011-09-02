# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        task = orm.ScheduledTask.objects.get(function='ecm.core.tasks.users.update_all_character_associations')
        task.is_active = False
        task.save()


    def backwards(self, orm):
        task = orm.ScheduledTask.objects.get(function='ecm.core.tasks.users.update_all_character_associations')
        task.is_active = True
        task.save()


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
            'next_execution': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 9, 1, 21, 1, 12, 776000)'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['scheduler']
