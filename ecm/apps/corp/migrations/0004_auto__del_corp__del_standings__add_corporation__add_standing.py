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

SQL_CURRENT_CORP = """SELECT 
    "taxRate", 
    "corporationID", 
    "description", 
    "memberLimit", 
    "allianceName", 
    "stationName", 
    "corporationName", 
    "ceoName", 
    "ticker", 
    "allianceTicker", 
    "stationID", 
    "allianceID", 
    "ceoID" 
FROM "corp_corp" 
WHERE "id" = 1;
"""

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        if not db.dry_run:
            sql = mysql_quotes(SQL_CURRENT_CORP)
            rows = db.execute(sql)
            if rows:
                (taxRate, corporationID, description, memberLimit, 
                 allianceName, stationName, corporationName, ceoName, 
                 ticker, allianceTicker, stationID, allianceID, ceoID) = rows[0]
                previous_corp = True
            else:
                previous_corp = False
            
            sql = mysql_quotes('SELECT "contactID", "contactName", "is_corp_contact", "standing" from "corp_standings";')
            standings_rows = db.execute(sql)
        
        # Deleting model 'Corp'
        db.delete_table('corp_corp')

        # Deleting model 'Standings'
        db.delete_table('corp_standings')

        # Adding model 'Corporation'
        db.create_table('corp_corporation', (
            ('ecm_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('is_my_corp', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('corporationID', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('corporationName', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('ticker', self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True)),
            ('ceoID', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('ceoName', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('stationID', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('stationName', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('allianceID', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('allianceName', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('allianceTicker', self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('taxRate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('memberLimit', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('private_key', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('public_key', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('key_fingerprint', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('corp', ['Corporation'])

        # Adding model 'Standing'
        db.create_table('corp_standing', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('corp', self.gf('django.db.models.fields.related.ForeignKey')(related_name='standings', to=orm['corp.Corporation'])),
            ('contactID', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('contactName', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_corp_contact', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('corp', ['Standing'])

        if not db.dry_run and previous_corp:
            corp = orm.Corporation.objects.create(corporationID=corporationID, 
                                                  taxRate=taxRate, 
                                                  description=description, 
                                                  memberLimit=memberLimit, 
                                                  allianceName=allianceName, 
                                                  stationName=stationName, 
                                                  corporationName=corporationName, 
                                                  ceoName=ceoName, 
                                                  ticker=ticker, 
                                                  allianceTicker=allianceTicker, 
                                                  stationID=stationID, 
                                                  allianceID=allianceID, 
                                                  ceoID=ceoID,
                                                  is_my_corp=True,
                                                  ecm_url=None,
                                                  private_key=None,
                                                  public_key=None,
                                                  key_fingerprint=None)

            for contactID, contactName, is_corp_contact, standing in standings_rows:
                orm.Standing.objects.create(corp=corp,
                                            contactID=contactID,
                                            contactName=contactName,
                                            is_corp_contact=is_corp_contact,
                                            value=standing,
                                            )


    def backwards(self, orm):
        # Adding model 'Corp'
        db.create_table('corp_corp', (
            ('taxRate', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('corporationID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('memberLimit', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('allianceName', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('stationName', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('corporationName', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('ceoName', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('ticker', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('allianceTicker', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('stationID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('allianceID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('ceoID', self.gf('django.db.models.fields.BigIntegerField')()),
        ))
        db.send_create_signal('corp', ['Corp'])

        # Adding model 'Standings'
        db.create_table('corp_standings', (
            ('standing', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('is_corp_contact', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('contactID', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('contactName', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('corp', ['Standings'])

        # Deleting model 'Corporation'
        db.delete_table('corp_corporation')

        # Deleting model 'Standing'
        db.delete_table('corp_standing')


    models = {
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
        'corp.hangar': {
            'Meta': {'ordering': "['hangarID']", 'object_name': 'Hangar'},
            'accessLvl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'hangarID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
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
            'accessLvl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'walletID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['corp']
