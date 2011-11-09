# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Pricing'
        db.create_table('industry_pricing', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('margin', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('industry', ['Pricing'])

        # Adding model 'CatalogEntry'
        db.create_table('industry_catalogentry', (
            ('typeID', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('typeName', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('marketGroupID', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('fixedPrice', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('isAvailable', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('industry', ['CatalogEntry'])

        # Adding model 'OwnedBlueprint'
        db.create_table('industry_ownedblueprint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('blueprintTypeID', self.gf('django.db.models.fields.IntegerField')()),
            ('me', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('pe', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('copy', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('runs', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('catalogEntry', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='blueprints', null=True, to=orm['industry.CatalogEntry'])),
        ))
        db.send_create_signal('industry', ['OwnedBlueprint'])

        # Adding model 'SupplyPrice'
        db.create_table('industry_supplyprice', (
            ('typeID', self.gf('django.db.models.fields.PositiveIntegerField')(primary_key=True)),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('autoUpdate', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('industry', ['SupplyPrice'])

        # Adding model 'PriceHistory'
        db.create_table('industry_pricehistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('typeID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('industry', ['PriceHistory'])

        # Adding model 'InventionPolicy'
        db.create_table('industry_inventionpolicy', (
            ('itemGroupID', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('itemGroupName', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('inventionChance', self.gf('django.db.models.fields.FloatField')()),
            ('targetME', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('industry', ['InventionPolicy'])

        # Adding model 'Job'
        db.create_table('industry_job', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='jobs', null=True, to=orm['industry.Order'])),
            ('row', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='jobs', null=True, to=orm['industry.OrderRow'])),
            ('parentJob', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='childrenJobs', null=True, to=orm['industry.Job'])),
            ('state', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='jobs', null=True, to=orm['auth.User'])),
            ('itemID', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('runs', self.gf('django.db.models.fields.FloatField')()),
            ('blueprint', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='jobs', null=True, to=orm['industry.OwnedBlueprint'])),
            ('activity', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('dueDate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('startDate', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('endDate', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('industry', ['Job'])

        # Adding model 'Order'
        db.create_table('industry_order', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('originator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='orders_created', to=orm['auth.User'])),
            ('manufacturer', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='orders_manufactured', null=True, to=orm['auth.User'])),
            ('deliveryMan', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='orders_delivered', null=True, to=orm['auth.User'])),
            ('client', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('deliveryLocation', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('deliveryDate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('quote', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('pricing', self.gf('django.db.models.fields.related.ForeignKey')(related_name='orders', to=orm['industry.Pricing'])),
            ('extraDiscount', self.gf('django.db.models.fields.FloatField')(default=0.0)),
        ))
        db.send_create_signal('industry', ['Order'])

        # Adding model 'OrderLog'
        db.create_table('industry_orderlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='logs', to=orm['industry.Order'])),
            ('state', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='logs', to=orm['auth.User'])),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('industry', ['OrderLog'])

        # Adding model 'OrderRow'
        db.create_table('industry_orderrow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rows', to=orm['industry.Order'])),
            ('catalogEntry', self.gf('django.db.models.fields.related.ForeignKey')(related_name='order_rows', to=orm['industry.CatalogEntry'])),
            ('quantity', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('cost', self.gf('django.db.models.fields.FloatField')(default=0.0)),
        ))
        db.send_create_signal('industry', ['OrderRow'])


    def backwards(self, orm):
        
        # Deleting model 'Pricing'
        db.delete_table('industry_pricing')

        # Deleting model 'CatalogEntry'
        db.delete_table('industry_catalogentry')

        # Deleting model 'OwnedBlueprint'
        db.delete_table('industry_ownedblueprint')

        # Deleting model 'SupplyPrice'
        db.delete_table('industry_supplyprice')

        # Deleting model 'PriceHistory'
        db.delete_table('industry_pricehistory')

        # Deleting model 'InventionPolicy'
        db.delete_table('industry_inventionpolicy')

        # Deleting model 'Job'
        db.delete_table('industry_job')

        # Deleting model 'Order'
        db.delete_table('industry_order')

        # Deleting model 'OrderLog'
        db.delete_table('industry_orderlog')

        # Deleting model 'OrderRow'
        db.delete_table('industry_orderrow')


    models = {
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
        },
        'industry.catalogentry': {
            'Meta': {'object_name': 'CatalogEntry'},
            'fixedPrice': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'isAvailable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'marketGroupID': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'typeID': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'typeName': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'industry.inventionpolicy': {
            'Meta': {'ordering': "['targetME', 'itemGroupID']", 'object_name': 'InventionPolicy'},
            'inventionChance': ('django.db.models.fields.FloatField', [], {}),
            'itemGroupID': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'itemGroupName': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'targetME': ('django.db.models.fields.IntegerField', [], {})
        },
        'industry.job': {
            'Meta': {'ordering': "['order', 'id']", 'object_name': 'Job'},
            'activity': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'blueprint': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'jobs'", 'null': 'True', 'to': "orm['industry.OwnedBlueprint']"}),
            'dueDate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'endDate': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'itemID': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'jobs'", 'null': 'True', 'to': "orm['industry.Order']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'jobs'", 'null': 'True', 'to': "orm['auth.User']"}),
            'parentJob': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'childrenJobs'", 'null': 'True', 'to': "orm['industry.Job']"}),
            'row': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'jobs'", 'null': 'True', 'to': "orm['industry.OrderRow']"}),
            'runs': ('django.db.models.fields.FloatField', [], {}),
            'startDate': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'industry.order': {
            'Meta': {'ordering': "['id']", 'object_name': 'Order'},
            'client': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'deliveryDate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'deliveryLocation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'deliveryMan': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'orders_delivered'", 'null': 'True', 'to': "orm['auth.User']"}),
            'extraDiscount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'orders_manufactured'", 'null': 'True', 'to': "orm['auth.User']"}),
            'originator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'orders_created'", 'to': "orm['auth.User']"}),
            'pricing': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'orders'", 'to': "orm['industry.Pricing']"}),
            'quote': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'state': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'industry.orderlog': {
            'Meta': {'ordering': "['order', 'date']", 'object_name': 'OrderLog'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'logs'", 'to': "orm['industry.Order']"}),
            'state': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'logs'", 'to': "orm['auth.User']"})
        },
        'industry.orderrow': {
            'Meta': {'ordering': "['order']", 'object_name': 'OrderRow'},
            'catalogEntry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_rows'", 'to': "orm['industry.CatalogEntry']"}),
            'cost': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rows'", 'to': "orm['industry.Order']"}),
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'industry.ownedblueprint': {
            'Meta': {'ordering': "['blueprintTypeID', '-me']", 'object_name': 'OwnedBlueprint'},
            'blueprintTypeID': ('django.db.models.fields.IntegerField', [], {}),
            'catalogEntry': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'blueprints'", 'null': 'True', 'to': "orm['industry.CatalogEntry']"}),
            'copy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'me': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'pe': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'runs': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'})
        },
        'industry.pricehistory': {
            'Meta': {'ordering': "['typeID', 'date']", 'object_name': 'PriceHistory'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'typeID': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'industry.pricing': {
            'Meta': {'object_name': 'Pricing'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'margin': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'industry.supplyprice': {
            'Meta': {'ordering': "['typeID']", 'object_name': 'SupplyPrice'},
            'autoUpdate': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'typeID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['industry']
