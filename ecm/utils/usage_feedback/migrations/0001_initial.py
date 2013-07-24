#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ECMInstanceFeedback'
        db.create_table(u'usage_feedback_ecminstancefeedback', (
            ('key_fingerprint', self.gf('django.db.models.fields.CharField')(max_length=200, primary_key=True)),
            ('active_user_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('avg_last_visit_top10', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('avg_last_visit', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('first_installed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('country_code', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('country_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('feedback_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'usage_feedback', ['ECMInstanceFeedback'])


    def backwards(self, orm):
        # Deleting model 'ECMInstanceFeedback'
        db.delete_table(u'usage_feedback_ecminstancefeedback')


    models = {
        u'usage_feedback.ecminstancefeedback': {
            'Meta': {'object_name': 'ECMInstanceFeedback'},
            'active_user_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'avg_last_visit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'avg_last_visit_top10': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'country_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'feedback_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'first_installed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'key_fingerprint': ('django.db.models.fields.CharField', [], {'max_length': '200', 'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['usage_feedback']