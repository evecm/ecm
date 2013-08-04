#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ECMInstanceFeedback.version'
        db.add_column(u'usage_feedback_ecminstancefeedback', 'version',
                      self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ECMInstanceFeedback.version'
        db.delete_column(u'usage_feedback_ecminstancefeedback', 'version')


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
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['usage_feedback']