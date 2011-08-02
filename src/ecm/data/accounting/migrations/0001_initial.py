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
        
        # Adding model 'EntryType'
        db.create_table('accounting_entrytype', (
            ('refTypeID', self.gf('django.db.models.fields.PositiveIntegerField')(primary_key=True)),
            ('refTypeName', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('accounting', ['EntryType'])

        # Adding model 'JournalEntry'
        db.create_table('accounting_journalentry', (
            ('id', self.gf('ecm.lib.bigintpatch.BigAutoField')(primary_key=True)),
            ('refID', self.gf('django.db.models.fields.BigIntegerField')()),
            ('wallet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['corp.Wallet'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounting.EntryType'])),
            ('ownerName1', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('ownerID1', self.gf('django.db.models.fields.BigIntegerField')()),
            ('ownerName2', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('ownerID2', self.gf('django.db.models.fields.BigIntegerField')()),
            ('argName1', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('argID1', self.gf('django.db.models.fields.BigIntegerField')()),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('balance', self.gf('django.db.models.fields.FloatField')()),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal('accounting', ['JournalEntry'])


    def backwards(self, orm):
        
        # Deleting model 'EntryType'
        db.delete_table('accounting_entrytype')

        # Deleting model 'JournalEntry'
        db.delete_table('accounting_journalentry')


    models = {
        'accounting.entrytype': {
            'Meta': {'object_name': 'EntryType'},
            'refTypeID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'refTypeName': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'accounting.journalentry': {
            'Meta': {'object_name': 'JournalEntry'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'argID1': ('django.db.models.fields.BigIntegerField', [], {}),
            'argName1': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'balance': ('django.db.models.fields.FloatField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'ownerID1': ('django.db.models.fields.BigIntegerField', [], {}),
            'ownerID2': ('django.db.models.fields.BigIntegerField', [], {}),
            'ownerName1': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'ownerName2': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'refID': ('django.db.models.fields.BigIntegerField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounting.EntryType']"}),
            'wallet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corp.Wallet']"})
        },
        'corp.wallet': {
            'Meta': {'object_name': 'Wallet'},
            'accessLvl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'walletID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['accounting']
