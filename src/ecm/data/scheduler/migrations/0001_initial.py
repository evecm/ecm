# Copyright (c) 2010-2011 Robin Jarry
# 
# This file is part of EVE Corporation Management.
# 
# EVE Corporation Management is free software: you can redistribute it and/or 
# modify it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or (at your 
# option) any later version.
# 
# EVE Corporation Management is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
# more details.
# 
# You should have received a copy of the GNU General Public License along with 
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

# encoding: utf-8
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
            ('next_execution', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 7, 31, 4, 47, 58, 371000))),
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
            'next_execution': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 7, 31, 4, 47, 58, 371000)'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['scheduler']
