#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'ScheduledTask'
        db.create_table('scheduler_scheduledtask', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('function', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('args', self.gf('django.db.models.fields.CharField')(default='{}', max_length=256)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('next_execution', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 10, 26, 0, 53, 37, 20000))),
            ('frequency', self.gf('django.db.models.fields.IntegerField')()),
            ('frequency_units', self.gf('django.db.models.fields.IntegerField')(default=3600)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_running', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_one_shot', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_last_exec_success', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('scheduler', ['ScheduledTask'])

        # Adding model 'GarbageCollector'
        db.create_table('scheduler_garbagecollector', (
            ('db_table', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('min_entries_threshold', self.gf('django.db.models.fields.BigIntegerField')(default=10000)),
            ('max_age_threshold', self.gf('django.db.models.fields.BigIntegerField')()),
            ('age_units', self.gf('django.db.models.fields.BigIntegerField')(default=18144000)),
        ))
        db.send_create_signal('scheduler', ['GarbageCollector'])


    def backwards(self, orm):

        # Deleting model 'ScheduledTask'
        db.delete_table('scheduler_scheduledtask')

        # Deleting model 'GarbageCollector'
        db.delete_table('scheduler_garbagecollector')


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
            'next_execution': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 10, 26, 0, 53, 37, 20000)'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['scheduler']
