# encoding: utf-8
import time
import atom
from south.db import db
from south.v2 import DataMigration
from videos.types.youtube import YouTubeApiBridge

import logging

class Migration(DataMigration):
    
    def forwards(self, orm):
        if not db.dry_run:
            for account in orm.ThirdPartyAccount.objects.filter(type='Y').all():
                bridge = YouTubeApiBridge(account.oauth_access_token, 
                                          account.oauth_refresh_token, '')

                try:
                    feed = bridge.get_user_profile('default')
                    author = [x for x in feed.get_elements() if type(x) == atom.data.Author][0]
                    username = [x for x in feed.get_elements() if x.tag == 'username'][0].text
                except Exception:
                    logging.exception("Could not login account %s" % account.username)
                    continue

                if username:
                    account.username = username.decode("utf-8")

                if author:
                    account.full_name = author.name.text

                try:
                    account.save()
                except Exception, e:
                    print "error - could not migrate account %s" % e

                time.sleep(1)
    
    def backwards(self, orm):
        if not db.dry_run:
            for account in orm.ThirdPartyAccount.objects.filter(type='Y').all():
                bridge = YouTubeApiBridge(account.oauth_access_token, 
                                          account.oauth_refresh_token, '')

                try:
                    feed = bridge.get_user_profile('default')
                    author = [x for x in feed.get_elements() if type(x) == atom.data.Author][0]
                except Exception:
                    logging.exception("Could not login account %s" % account.username)
                    continue

                if author:
                    account.username = author.name.text

                try:
                    account.save()
                except Exception, e:
                    print "error - could not migrate account %s -> %s, %s" % (account.username, account.full_name, e)

                print "backwarded account %s" % account.username
                time.sleep(1)
    
    models = {
        'accountlinker.thirdpartyaccount': {
            'Meta': {'unique_together': "(('type', 'username'),)", 'object_name': 'ThirdPartyAccount'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oauth_access_token': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'oauth_refresh_token': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'accountlinker.youtubesyncrule': {
            'Meta': {'object_name': 'YoutubeSyncRule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'team': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'user': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'video': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'})
        }
    }
    
    complete_apps = ['accountlinker']
