# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting field 'WidgetDialogLog.draft_pk'
        db.delete_column('uslogging_widgetdialoglog', 'draft_pk')
    
    
    def backwards(self, orm):
        
        # Adding field 'WidgetDialogLog.draft_pk'
        db.add_column('uslogging_widgetdialoglog', 'draft_pk', self.gf('django.db.models.fields.IntegerField')(default=None), keep_default=False)
    
    
    models = {
        'uslogging.widgetdialogcall': {
            'Meta': {'object_name': 'WidgetDialogCall'},
            'browser_id': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'date_saved': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'request_args': ('django.db.models.fields.TextField', [], {})
        },
        'uslogging.widgetdialoglog': {
            'Meta': {'object_name': 'WidgetDialogLog'},
            'browser_id': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'date_saved': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log': ('django.db.models.fields.TextField', [], {})
        }
    }
    
    complete_apps = ['uslogging']
