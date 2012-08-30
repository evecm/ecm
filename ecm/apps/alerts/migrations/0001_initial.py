#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ObserverSpec'
        db.create_table('alerts_observerspec', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('app', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('handler_function', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('callback_function', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('arguments_spec', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('notification_type', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
        ))
        db.send_create_signal('alerts', ['ObserverSpec'])

        # Adding model 'Observer'
        db.create_table('alerts_observer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('observer_spec', self.gf('django.db.models.fields.related.ForeignKey')(related_name='observers', to=orm['alerts.ObserverSpec'])),
            ('arguments', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('notification_type', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('last_scan', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('alerts', ['Observer'])

        # Adding M2M table for field users on 'Observer'
        db.create_table('alerts_observer_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('observer', models.ForeignKey(orm['alerts.observer'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('alerts_observer_users', ['observer_id', 'user_id'])

        # Adding M2M table for field groups on 'Observer'
        db.create_table('alerts_observer_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('observer', models.ForeignKey(orm['alerts.observer'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('alerts_observer_groups', ['observer_id', 'group_id'])


    def backwards(self, orm):
        # Deleting model 'ObserverSpec'
        db.delete_table('alerts_observerspec')

        # Deleting model 'Observer'
        db.delete_table('alerts_observer')

        # Removing M2M table for field users on 'Observer'
        db.delete_table('alerts_observer_users')

        # Removing M2M table for field groups on 'Observer'
        db.delete_table('alerts_observer_groups')


    models = {
        'alerts.observer': {
            'Meta': {'object_name': 'Observer'},
            'arguments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'groups'", 'blank': 'True', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_scan': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'notification_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'observer_spec': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'observers'", 'to': "orm['alerts.ObserverSpec']"}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'users'", 'blank': 'True', 'to': "orm['auth.User']"})
        },
        'alerts.observerspec': {
            'Meta': {'object_name': 'ObserverSpec'},
            'app': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'arguments_spec': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'callback_function': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'handler_function': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'notification_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['alerts']