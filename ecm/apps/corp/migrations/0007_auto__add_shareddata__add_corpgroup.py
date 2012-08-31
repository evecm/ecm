#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SharedData'
        db.create_table('corp_shareddata', (
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('handler', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('corp', ['SharedData'])

        # Adding model 'CorpGroup'
        db.create_table('corp_corpgroup', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
        ))
        db.send_create_signal('corp', ['CorpGroup'])

        # Adding M2M table for field corporations on 'CorpGroup'
        db.create_table('corp_corpgroup_corporations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('corpgroup', models.ForeignKey(orm['corp.corpgroup'], null=False)),
            ('corporation', models.ForeignKey(orm['corp.corporation'], null=False))
        ))
        db.create_unique('corp_corpgroup_corporations', ['corpgroup_id', 'corporation_id'])

        # Adding M2M table for field allowed_shares on 'CorpGroup'
        db.create_table('corp_corpgroup_allowed_shares', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('corpgroup', models.ForeignKey(orm['corp.corpgroup'], null=False)),
            ('shareddata', models.ForeignKey(orm['corp.shareddata'], null=False))
        ))
        db.create_unique('corp_corpgroup_allowed_shares', ['corpgroup_id', 'shareddata_id'])


    def backwards(self, orm):
        # Deleting model 'SharedData'
        db.delete_table('corp_shareddata')

        # Deleting model 'CorpGroup'
        db.delete_table('corp_corpgroup')

        # Removing M2M table for field corporations on 'CorpGroup'
        db.delete_table('corp_corpgroup_corporations')

        # Removing M2M table for field allowed_shares on 'CorpGroup'
        db.delete_table('corp_corpgroup_allowed_shares')


    models = {
        'corp.corpgroup': {
            'Meta': {'object_name': 'CorpGroup'},
            'allowed_shares': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'shared_datas'", 'symmetrical': 'False', 'to': "orm['corp.SharedData']"}),
            'corporations': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'corp_groups'", 'symmetrical': 'False', 'to': "orm['corp.Corporation']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'})
        },
        'corp.corphangar': {
            'Meta': {'ordering': "('corp', 'hangar')", 'unique_together': "(('corp', 'hangar'),)", 'object_name': 'CorpHangar'},
            'access_lvl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'corp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hangars'", 'to': "orm['corp.Corporation']"}),
            'hangar': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corp_hangars'", 'to': "orm['corp.Hangar']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'corp.corporation': {
            'Meta': {'object_name': 'Corporation'},
            'allianceID': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'allianceName': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'allianceTicker': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'ceoID': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ceoName': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'corporationID': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'corporationName': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ecm_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'is_my_corp': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_trusted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key_fingerprint': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'memberLimit': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'private_key': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'public_key': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'stationID': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'stationName': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'taxRate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ticker': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'})
        },
        'corp.corpwallet': {
            'Meta': {'ordering': "('corp', 'wallet')", 'unique_together': "(('corp', 'wallet'),)", 'object_name': 'CorpWallet'},
            'access_lvl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'corp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wallets'", 'to': "orm['corp.Corporation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'wallet': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corp_wallets'", 'to': "orm['corp.Wallet']"})
        },
        'corp.hangar': {
            'Meta': {'ordering': "['hangarID']", 'object_name': 'Hangar'},
            'hangarID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'})
        },
        'corp.shareddata': {
            'Meta': {'object_name': 'SharedData'},
            'handler': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        'corp.standing': {
            'Meta': {'ordering': "('-value', 'contactName')", 'object_name': 'Standing'},
            'contactID': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'contactName': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'corp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'standings'", 'to': "orm['corp.Corporation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_corp_contact': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'corp.wallet': {
            'Meta': {'ordering': "['walletID']", 'object_name': 'Wallet'},
            'walletID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['corp']