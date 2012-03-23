#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Skill'
        db.create_table('hr_skill', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('character', self.gf('django.db.models.fields.related.ForeignKey')(related_name='skills', to=orm['hr.Member'])),
            ('typeID', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('skillpoints', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('level', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('hr', ['Skill'])

        # Adding field 'Member.DoB'
        db.add_column('hr_member', 'DoB', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True), keep_default=False)

        # Adding field 'Member.race'
        db.add_column('hr_member', 'race', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True), keep_default=False)

        # Adding field 'Member.bloodLine'
        db.add_column('hr_member', 'bloodLine', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True), keep_default=False)

        # Adding field 'Member.ancestry'
        db.add_column('hr_member', 'ancestry', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True), keep_default=False)

        # Adding field 'Member.gender'
        db.add_column('hr_member', 'gender', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True), keep_default=False)

        # Adding field 'Member.corporationName'
        db.add_column('hr_member', 'corporationName', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True), keep_default=False)

        # Adding field 'Member.corporationID'
        db.add_column('hr_member', 'corporationID', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)

        # Adding field 'Member.allianceName'
        db.add_column('hr_member', 'allianceName', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True), keep_default=False)

        # Adding field 'Member.allianceID'
        db.add_column('hr_member', 'allianceID', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)

        # Adding field 'Member.cloneName'
        db.add_column('hr_member', 'cloneName', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True), keep_default=False)

        # Adding field 'Member.cloneSkillPoints'
        db.add_column('hr_member', 'cloneSkillPoints', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)

        # Adding field 'Member.balance'
        db.add_column('hr_member', 'balance', self.gf('django.db.models.fields.FloatField')(default=0.0), keep_default=False)

        # Adding field 'Member.memoryBonusName'
        db.add_column('hr_member', 'memoryBonusName', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True), keep_default=False)

        # Adding field 'Member.memoryBonusValue'
        db.add_column('hr_member', 'memoryBonusValue', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)

        # Adding field 'Member.intelligenceBonusName'
        db.add_column('hr_member', 'intelligenceBonusName', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True), keep_default=False)

        # Adding field 'Member.intelligenceBonusValue'
        db.add_column('hr_member', 'intelligenceBonusValue', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)

        # Adding field 'Member.charismaBonusName'
        db.add_column('hr_member', 'charismaBonusName', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True), keep_default=False)

        # Adding field 'Member.charismaBonusValue'
        db.add_column('hr_member', 'charismaBonusValue', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)

        # Adding field 'Member.willpowerBonusName'
        db.add_column('hr_member', 'willpowerBonusName', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True), keep_default=False)

        # Adding field 'Member.willpowerBonusValue'
        db.add_column('hr_member', 'willpowerBonusValue', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)

        # Adding field 'Member.perceptionBonusName'
        db.add_column('hr_member', 'perceptionBonusName', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True), keep_default=False)

        # Adding field 'Member.perceptionBonusValue'
        db.add_column('hr_member', 'perceptionBonusValue', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)

        # Adding field 'Member.intelligence'
        db.add_column('hr_member', 'intelligence', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Member.memory'
        db.add_column('hr_member', 'memory', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Member.charisma'
        db.add_column('hr_member', 'charisma', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Member.perception'
        db.add_column('hr_member', 'perception', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Member.willpower'
        db.add_column('hr_member', 'willpower', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)


    def backwards(self, orm):

        # Deleting model 'Skill'
        db.delete_table('hr_skill')

        # Deleting field 'Member.DoB'
        db.delete_column('hr_member', 'DoB')

        # Deleting field 'Member.race'
        db.delete_column('hr_member', 'race')

        # Deleting field 'Member.bloodLine'
        db.delete_column('hr_member', 'bloodLine')

        # Deleting field 'Member.ancestry'
        db.delete_column('hr_member', 'ancestry')

        # Deleting field 'Member.gender'
        db.delete_column('hr_member', 'gender')

        # Deleting field 'Member.corporationName'
        db.delete_column('hr_member', 'corporationName')

        # Deleting field 'Member.corporationID'
        db.delete_column('hr_member', 'corporationID')

        # Deleting field 'Member.allianceName'
        db.delete_column('hr_member', 'allianceName')

        # Deleting field 'Member.allianceID'
        db.delete_column('hr_member', 'allianceID')

        # Deleting field 'Member.cloneName'
        db.delete_column('hr_member', 'cloneName')

        # Deleting field 'Member.cloneSkillPoints'
        db.delete_column('hr_member', 'cloneSkillPoints')

        # Deleting field 'Member.balance'
        db.delete_column('hr_member', 'balance')

        # Deleting field 'Member.memoryBonusName'
        db.delete_column('hr_member', 'memoryBonusName')

        # Deleting field 'Member.memoryBonusValue'
        db.delete_column('hr_member', 'memoryBonusValue')

        # Deleting field 'Member.intelligenceBonusName'
        db.delete_column('hr_member', 'intelligenceBonusName')

        # Deleting field 'Member.intelligenceBonusValue'
        db.delete_column('hr_member', 'intelligenceBonusValue')

        # Deleting field 'Member.charismaBonusName'
        db.delete_column('hr_member', 'charismaBonusName')

        # Deleting field 'Member.charismaBonusValue'
        db.delete_column('hr_member', 'charismaBonusValue')

        # Deleting field 'Member.willpowerBonusName'
        db.delete_column('hr_member', 'willpowerBonusName')

        # Deleting field 'Member.willpowerBonusValue'
        db.delete_column('hr_member', 'willpowerBonusValue')

        # Deleting field 'Member.perceptionBonusName'
        db.delete_column('hr_member', 'perceptionBonusName')

        # Deleting field 'Member.perceptionBonusValue'
        db.delete_column('hr_member', 'perceptionBonusValue')

        # Deleting field 'Member.intelligence'
        db.delete_column('hr_member', 'intelligence')

        # Deleting field 'Member.memory'
        db.delete_column('hr_member', 'memory')

        # Deleting field 'Member.charisma'
        db.delete_column('hr_member', 'charisma')

        # Deleting field 'Member.perception'
        db.delete_column('hr_member', 'perception')

        # Deleting field 'Member.willpower'
        db.delete_column('hr_member', 'willpower')


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
        'corp.hangar': {
            'Meta': {'ordering': "['hangarID']", 'object_name': 'Hangar'},
            'accessLvl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'hangarID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'corp.wallet': {
            'Meta': {'ordering': "['walletID']", 'object_name': 'Wallet'},
            'accessLvl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'walletID': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'})
        },
        'hr.member': {
            'DoB': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'Meta': {'ordering': "['name']", 'object_name': 'Member'},
            'accessLvl': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'allianceID': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'allianceName': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'ancestry': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'balance': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'baseID': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'bloodLine': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'characterID': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'charisma': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'charismaBonusName': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'charismaBonusValue': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cloneName': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'cloneSkillPoints': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'corpDate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 3, 16, 15, 43, 57, 257000)'}),
            'corped': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'corporationID': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'corporationName': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'intelligence': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'intelligenceBonusName': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'intelligenceBonusValue': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'lastLogin': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 3, 16, 15, 43, 57, 258000)'}),
            'lastLogoff': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 3, 16, 15, 43, 57, 258000)'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "'???'", 'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'locationID': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'memory': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'memoryBonusName': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'memoryBonusValue': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'characters'", 'null': 'True', 'to': "orm['auth.User']"}),
            'perception': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'perceptionBonusName': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'perceptionBonusValue': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'race': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'ship': ('django.db.models.fields.CharField', [], {'default': "'???'", 'max_length': '128'}),
            'willpower': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'willpowerBonusName': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'willpowerBonusValue': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'hr.memberdiff': {
            'Meta': {'ordering': "['date']", 'object_name': 'MemberDiff'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 3, 16, 15, 43, 57, 260000)', 'db_index': 'True'}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'diffs'", 'to': "orm['hr.Member']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'new': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'})
        },
        'hr.membersession': {
            'Meta': {'ordering': "['session_begin']", 'object_name': 'MemberSession'},
            'character_id': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'session_begin': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'session_end': ('django.db.models.fields.DateTimeField', [], {}),
            'session_seconds': ('django.db.models.fields.BigIntegerField', [], {'default': '0'})
        },
        'hr.role': {
            'Meta': {'ordering': "['id']", 'object_name': 'Role'},
            'accessLvl': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'dispName': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'hangar': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corp.Hangar']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'roles'", 'symmetrical': 'False', 'through': "orm['hr.RoleMembership']", 'to': "orm['hr.Member']"}),
            'roleID': ('django.db.models.fields.BigIntegerField', [], {}),
            'roleName': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'roleType': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': "orm['hr.RoleType']"}),
            'wallet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['corp.Wallet']", 'null': 'True', 'blank': 'True'})
        },
        'hr.rolememberdiff': {
            'Meta': {'ordering': "['date']", 'object_name': 'RoleMemberDiff'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 3, 16, 15, 43, 57, 269000)', 'db_index': 'True'}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Member']"}),
            'new': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Role']"})
        },
        'hr.rolemembership': {
            'Meta': {'ordering': "['member']", 'object_name': 'RoleMembership'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Member']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Role']"})
        },
        'hr.roletype': {
            'Meta': {'ordering': "['dispName']", 'object_name': 'RoleType'},
            'dispName': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'typeName': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'hr.skill': {
            'Meta': {'object_name': 'Skill'},
            'character': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'skills'", 'to': "orm['hr.Member']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'skillpoints': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'typeID': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'hr.title': {
            'Meta': {'ordering': "['titleID']", 'object_name': 'Title'},
            'accessLvl': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'titles'", 'symmetrical': 'False', 'through': "orm['hr.TitleMembership']", 'to': "orm['hr.Member']"}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'titles'", 'symmetrical': 'False', 'through': "orm['hr.TitleComposition']", 'to': "orm['hr.Role']"}),
            'tiedToBase': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'titleID': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'titleName': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'hr.titlecompodiff': {
            'Meta': {'ordering': "['date']", 'object_name': 'TitleCompoDiff'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 3, 16, 15, 43, 57, 275000)', 'db_index': 'True'}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'new': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Role']"}),
            'title': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Title']"})
        },
        'hr.titlecomposition': {
            'Meta': {'ordering': "['title']", 'object_name': 'TitleComposition'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Role']"}),
            'title': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Title']"})
        },
        'hr.titlememberdiff': {
            'Meta': {'ordering': "['date']", 'object_name': 'TitleMemberDiff'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 3, 16, 15, 43, 57, 275000)', 'db_index': 'True'}),
            'id': ('ecm.lib.bigintpatch.BigAutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Member']"}),
            'new': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'title': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Title']"})
        },
        'hr.titlemembership': {
            'Meta': {'ordering': "['member']", 'object_name': 'TitleMembership'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Member']"}),
            'title': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Title']"})
        }
    }

    complete_apps = ['hr']
