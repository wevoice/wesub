# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

# mysql is barfing on the longer index name

key_name = 'accountlinker_tpa'
class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'ThirdPartyAccount'
        db.create_table('accountlinker_thirdpartyaccount', (
            ('username', self.gf('django.db.models.fields.CharField')(max_length=512, db_index=True)),
            ('oauth_refresh_token', self.gf('django.db.models.fields.CharField')(max_length=256, db_index=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('oauth_access_token', self.gf('django.db.models.fields.CharField')(max_length=256, db_index=True)),
        ))
        db.send_create_signal('accountlinker', ['ThirdPartyAccount'])

        # Adding unique constraint on 'ThirdPartyAccount', fields ['type', 'oauth_access_token']
        db.create_unique(key_name, ['type', 'oauth_access_token'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'ThirdPartyAccount'
        db.delete_table('accountlinker_thirdpartyaccount')

        # Removing unique constraint on 'ThirdPartyAccount', fields ['type', 'oauth_access_token']
        db.delete_unique(key_name, ['type', 'oauth_access_token'])
    
    
    models = {
        'accountlinker.thirdpartyaccount': {
            'Meta': {'unique_together': "(('type', 'oauth_access_token'),)", 'object_name': 'ThirdPartyAccount'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oauth_access_token': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'}),
            'oauth_refresh_token': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '512', 'db_index': 'True'})
        }
    }
    
    complete_apps = ['accountlinker']
