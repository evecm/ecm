# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Motd'
        db.create_table('common_motd', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.TextField')(default='MOTD Text')),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('markup', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
        ))
        db.send_create_signal('common', ['Motd'])


    def backwards(self, orm):
        
        # Deleting model 'Motd'
        db.delete_table('common_motd')


    complete_apps = ['common']