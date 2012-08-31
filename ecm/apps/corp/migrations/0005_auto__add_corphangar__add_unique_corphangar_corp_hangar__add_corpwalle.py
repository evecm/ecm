#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

def mysql_quotes(sql):
    if 'mysql' in db.backend_name.lower():
        return sql.replace('"', '`')
    else:
        return sql
    

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        if not db.dry_run:
            hangar_rows = db.execute(mysql_quotes('SELECT "hangarID", "name", "accessLvl" FROM "corp_hangar";'))
            wallet_rows = db.execute(mysql_quotes('SELECT "walletID", "name", "accessLvl" FROM "corp_wallet";'))
        
        # Adding model 'CorpHangar'
        db.create_table('corp_corphangar', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('corp', self.gf('django.db.models.fields.related.ForeignKey')(related_name='hangars', to=orm['corp.Corporation'])),
            ('hangar', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['corp.Hangar'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('access_lvl', self.gf('django.db.models.fields.PositiveIntegerField')(default=1000)),
        ))
        db.send_create_signal('corp', ['CorpHangar'])

        # Adding unique constraint on 'CorpHangar', fields ['corp', 'hangar']
        db.create_unique('corp_corphangar', ['corp_id', 'hangar_id'])

        # Adding model 'CorpWallet'
        db.create_table('corp_corpwallet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('corp', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wallet', to=orm['corp.Corporation'])),
            ('wallet', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['corp.Wallet'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('access_lvl', self.gf('django.db.models.fields.PositiveIntegerField')(default=1000)),
        ))
        db.send_create_signal('corp', ['CorpWallet'])

        # Adding unique constraint on 'CorpWallet', fields ['corp', 'wallet']
        db.create_unique('corp_corpwallet', ['corp_id', 'wallet_id'])

        # Deleting field 'Hangar.accessLvl'
        db.delete_column('corp_hangar', 'accessLvl')

        # Deleting field 'Hangar.name'
        db.delete_column('corp_hangar', 'name')

        # Deleting field 'Wallet.accessLvl'
        db.delete_column('corp_wallet', 'accessLvl')

        # Deleting field 'Wallet.name'
        db.delete_column('corp_wallet', 'name')

        if not db.dry_run:
            
            try:
                my_corp = orm.Corporation.objects.get(is_my_corp=True)
                
                for hangarID, name, access_lvl in hangar_rows:
                    hangar = orm.Hangar.objects.get(hangarID=hangarID)
                    orm.CorpHangar.objects.create(corp=my_corp, hangar=hangar, name=name, access_lvl=access_lvl)
                
                for walletID, name, access_lvl in wallet_rows:
                    wallet = orm.Wallet.objects.get(walletID=walletID)
                    orm.CorpWallet.objects.create(corp=my_corp, wallet=wallet, name=name, access_lvl=access_lvl)
            except orm.Corporation.DoesNotExist:
                pass
            

    def backwards(self, orm):
                
        # Removing unique constraint on 'CorpWallet', fields ['corp', 'wallet']
        db.delete_unique('corp_corpwallet', ['corp_id', 'wallet_id'])

        # Removing unique constraint on 'CorpHangar', fields ['corp', 'hangar']
        db.delete_unique('corp_corphangar', ['corp_id', 'hangar_id'])

        # Deleting model 'CorpHangar'
        db.delete_table('corp_corphangar')

        # Deleting model 'CorpWallet'
        db.delete_table('corp_corpwallet')

        # Adding field 'Hangar.accessLvl'
        db.add_column('corp_hangar', 'accessLvl',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=1000),
                      keep_default=False)

        # Adding field 'Hangar.name'
        db.add_column('corp_hangar', 'name',
                      self.gf('django.db.models.fields.CharField')(default='N/A', max_length=128),
                      keep_default=False)

        # Adding field 'Wallet.accessLvl'
        db.add_column('corp_wallet', 'accessLvl',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=1000),
                      keep_default=False)

        # Adding field 'Wallet.name'
        db.add_column('corp_wallet', 'name',
                      self.gf('django.db.models.fields.CharField')(default='N/A', max_length=128),
                      keep_default=False)

    models = {
        'corp.corphangar': {
            'Meta': {'ordering': "('corp', 'hangar')", 'unique_together': "(('corp', 'hangar'),)", 'object_name': 'CorpHangar'},
            'access_lvl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'corp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hangars'", 'to': "orm['corp.Corporation']"}),
            'hangar': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['corp.Hangar']"}),
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
            'corp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wallet'", 'to': "orm['corp.Corporation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'wallet': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['corp.Wallet']"})
        },
        'corp.hangar': {
            'Meta': {'ordering': "['hangarID']", 'object_name': 'Hangar'},
            'hangarID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'})
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