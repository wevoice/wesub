# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Video'
        db.create_table('videos_video', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('video_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=2048, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('duration', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('allow_community_edits', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_video_urls_edit', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('writelock_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('writelock_session_key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('writelock_owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='writelock_owners', null=True, to=orm['auth.CustomUser'])),
            ('is_subtitled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('was_subtitled', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('thumbnail', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('small_thumbnail', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('s3_thumbnail', self.gf('utils.amazon.fields.S3EnabledImageField')(max_length=100, thumb_sizes=((480, 270), (288, 162), (120, 90)), blank=True)),
            ('edited', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.CustomUser'], null=True, blank=True)),
            ('complete_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('featured', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('meta_1_type', self.gf('videos.metadata.MetadataTypeField')(null=True, blank=True)),
            ('meta_1_content', self.gf('videos.metadata.MetadataContentField')(default='', max_length=255, blank=True)),
            ('meta_2_type', self.gf('videos.metadata.MetadataTypeField')(null=True, blank=True)),
            ('meta_2_content', self.gf('videos.metadata.MetadataContentField')(default='', max_length=255, blank=True)),
            ('meta_3_type', self.gf('videos.metadata.MetadataTypeField')(null=True, blank=True)),
            ('meta_3_content', self.gf('videos.metadata.MetadataContentField')(default='', max_length=255, blank=True)),
            ('view_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True)),
            ('languages_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True)),
            ('moderated_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='moderating', null=True, to=orm['teams.Team'])),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('primary_audio_language_code', self.gf('django.db.models.fields.CharField')(default='', max_length=16, blank=True)),
        ))
        db.send_create_signal('videos', ['Video'])

        # Adding M2M table for field followers on 'Video'
        db.create_table('videos_video_followers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('video', models.ForeignKey(orm['videos.video'], null=False)),
            ('customuser', models.ForeignKey(orm['auth.customuser'], null=False))
        ))
        db.create_unique('videos_video_followers', ['video_id', 'customuser_id'])

        # Adding model 'VideoIndex'
        db.create_table('videos_videoindex', (
            ('video', self.gf('django.db.models.fields.related.OneToOneField')(related_name='index', unique=True, primary_key=True, to=orm['videos.Video'])),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('videos', ['VideoIndex'])

        # Adding model 'VideoMetadata'
        db.create_table('videos_videometadata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.Video'])),
            ('key', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('videos', ['VideoMetadata'])

        # Adding model 'SubtitleLanguage'
        db.create_table('videos_subtitlelanguage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.Video'])),
            ('is_original', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('writelock_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('writelock_session_key', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('writelock_owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.CustomUser'], null=True, blank=True)),
            ('is_complete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('subtitle_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('has_version', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('had_version', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_forked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('percent_done', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('standard_language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.SubtitleLanguage'], null=True, blank=True)),
            ('needs_sync', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('new_subtitle_language', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='old_subtitle_version', null=True, to=orm['subtitles.SubtitleLanguage'])),
        ))
        db.send_create_signal('videos', ['SubtitleLanguage'])

        # Adding unique constraint on 'SubtitleLanguage', fields ['video', 'language', 'standard_language']
        db.create_unique('videos_subtitlelanguage', ['video_id', 'language', 'standard_language_id'])

        # Adding M2M table for field followers on 'SubtitleLanguage'
        db.create_table('videos_subtitlelanguage_followers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('subtitlelanguage', models.ForeignKey(orm['videos.subtitlelanguage'], null=False)),
            ('customuser', models.ForeignKey(orm['auth.customuser'], null=False))
        ))
        db.create_unique('videos_subtitlelanguage_followers', ['subtitlelanguage_id', 'customuser_id'])

        # Adding model 'SubtitleVersion'
        db.create_table('videos_subtitleversion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.SubtitleLanguage'])),
            ('version_no', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('datetime_started', self.gf('django.db.models.fields.DateTimeField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.CustomUser'])),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('time_change', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('text_change', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('notification_sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('result_of_rollback', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('forked_from', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.SubtitleVersion'], null=True, blank=True)),
            ('is_forked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('moderation_status', self.gf('django.db.models.fields.CharField')(default='not__under_moderation', max_length=32, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=2048, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('needs_sync', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('new_subtitle_version', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='old_subtitle_version', unique=True, null=True, to=orm['subtitles.SubtitleVersion'])),
        ))
        db.send_create_signal('videos', ['SubtitleVersion'])

        # Adding unique constraint on 'SubtitleVersion', fields ['language', 'version_no']
        db.create_unique('videos_subtitleversion', ['language_id', 'version_no'])

        # Adding model 'SubtitleVersionMetadata'
        db.create_table('videos_subtitleversionmetadata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('data', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('subtitle_version', self.gf('django.db.models.fields.related.ForeignKey')(related_name='metadata', to=orm['videos.SubtitleVersion'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('videos', ['SubtitleVersionMetadata'])

        # Adding unique constraint on 'SubtitleVersionMetadata', fields ['key', 'subtitle_version']
        db.create_unique('videos_subtitleversionmetadata', ['key', 'subtitle_version_id'])

        # Adding model 'Subtitle'
        db.create_table('videos_subtitle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.SubtitleVersion'], null=True)),
            ('subtitle_id', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('subtitle_order', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('subtitle_text', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('start_time_seconds', self.gf('django.db.models.fields.FloatField')(null=True, db_column='start_time')),
            ('start_time', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, db_column='start_time_ms')),
            ('end_time_seconds', self.gf('django.db.models.fields.FloatField')(null=True, db_column='end_time')),
            ('end_time', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, db_column='end_time_ms')),
            ('start_of_paragraph', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('videos', ['Subtitle'])

        # Adding unique constraint on 'Subtitle', fields ['version', 'subtitle_id']
        db.create_unique('videos_subtitle', ['version_id', 'subtitle_id'])

        # Adding model 'SubtitleMetadata'
        db.create_table('videos_subtitlemetadata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subtitle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.Subtitle'])),
            ('key', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('videos', ['SubtitleMetadata'])

        # Adding model 'Action'
        db.create_table('videos_action', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.CustomUser'], null=True, blank=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.Video'], null=True, blank=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.SubtitleLanguage'], null=True, blank=True)),
            ('new_language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subtitles.SubtitleLanguage'], null=True, blank=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teams.Team'], null=True, blank=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teams.TeamMember'], null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['comments.Comment'], null=True, blank=True)),
            ('action_type', self.gf('django.db.models.fields.IntegerField')()),
            ('new_video_title', self.gf('django.db.models.fields.CharField')(max_length=2048, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
        ))
        db.send_create_signal('videos', ['Action'])

        # Adding model 'UserTestResult'
        db.create_table('videos_usertestresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('browser', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('task1', self.gf('django.db.models.fields.TextField')()),
            ('task2', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('task3', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('get_updates', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('videos', ['UserTestResult'])

        # Adding model 'VideoUrl'
        db.create_table('videos_videourl', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.Video'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=512)),
            ('videoid', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('primary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('original', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('added_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.CustomUser'], null=True, blank=True)),
            ('owner_username', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('videos', ['VideoUrl'])

        # Adding model 'VideoFeed'
        db.create_table('videos_videofeed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.CustomUser'], null=True, blank=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teams.Team'], null=True, blank=True)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('videos', ['VideoFeed'])

        # Adding model 'ImportedVideo'
        db.create_table('videos_importedvideo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.VideoFeed'])),
            ('video', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['videos.Video'], unique=True)),
        ))
        db.send_create_signal('videos', ['ImportedVideo'])

        # Adding model 'VideoTypeUrlPattern'
        db.create_table('videos_videotypeurlpattern', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('url_pattern', self.gf('django.db.models.fields.URLField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('videos', ['VideoTypeUrlPattern'])

    def backwards(self, orm):
        # Removing unique constraint on 'Subtitle', fields ['version', 'subtitle_id']
        db.delete_unique('videos_subtitle', ['version_id', 'subtitle_id'])

        # Removing unique constraint on 'SubtitleVersionMetadata', fields ['key', 'subtitle_version']
        db.delete_unique('videos_subtitleversionmetadata', ['key', 'subtitle_version_id'])

        # Removing unique constraint on 'SubtitleVersion', fields ['language', 'version_no']
        db.delete_unique('videos_subtitleversion', ['language_id', 'version_no'])

        # Removing unique constraint on 'SubtitleLanguage', fields ['video', 'language', 'standard_language']
        db.delete_unique('videos_subtitlelanguage', ['video_id', 'language', 'standard_language_id'])

        # Deleting model 'Video'
        db.delete_table('videos_video')

        # Removing M2M table for field followers on 'Video'
        db.delete_table('videos_video_followers')

        # Deleting model 'VideoIndex'
        db.delete_table('videos_videoindex')

        # Deleting model 'VideoMetadata'
        db.delete_table('videos_videometadata')

        # Deleting model 'SubtitleLanguage'
        db.delete_table('videos_subtitlelanguage')

        # Removing M2M table for field followers on 'SubtitleLanguage'
        db.delete_table('videos_subtitlelanguage_followers')

        # Deleting model 'SubtitleVersion'
        db.delete_table('videos_subtitleversion')

        # Deleting model 'SubtitleVersionMetadata'
        db.delete_table('videos_subtitleversionmetadata')

        # Deleting model 'Subtitle'
        db.delete_table('videos_subtitle')

        # Deleting model 'SubtitleMetadata'
        db.delete_table('videos_subtitlemetadata')

        # Deleting model 'Action'
        db.delete_table('videos_action')

        # Deleting model 'UserTestResult'
        db.delete_table('videos_usertestresult')

        # Deleting model 'VideoUrl'
        db.delete_table('videos_videourl')

        # Deleting model 'VideoFeed'
        db.delete_table('videos_videofeed')

        # Deleting model 'ImportedVideo'
        db.delete_table('videos_importedvideo')

        # Deleting model 'VideoTypeUrlPattern'
        db.delete_table('videos_videotypeurlpattern')

    models = {
        'auth.customuser': {
            'Meta': {'object_name': 'CustomUser', '_ormbases': ['auth.User']},
            'allow_3rd_party_login': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'autoplay_preferences': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'award_points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'biography': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'can_send_messages': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_users'", 'null': 'True', 'to': "orm['auth.CustomUser']"}),
            'full_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '63', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'is_partner': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'notify_by_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'notify_by_message': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'partner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.Partner']", 'null': 'True', 'blank': 'True'}),
            'pay_rate_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '3', 'blank': 'True'}),
            'picture': ('utils.amazon.fields.S3EnabledImageField', [], {'max_length': '100', 'blank': 'True'}),
            'playback_mode': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'preferred_language': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'show_tutorial': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'valid_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'videos': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['videos.Video']", 'symmetrical': 'False', 'blank': 'True'})
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
        'comments.comment': {
            'Meta': {'ordering': "('-submit_date',)", 'object_name': 'Comment'},
            'content': ('django.db.models.fields.TextField', [], {'max_length': '3000'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_comment'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_pk': ('django.db.models.fields.TextField', [], {}),
            'reply_to': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['comments.Comment']", 'null': 'True', 'blank': 'True'}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'subtitles.subtitlelanguage': {
            'Meta': {'unique_together': "[('video', 'language_code')]", 'object_name': 'SubtitleLanguage'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'new_followed_languages'", 'blank': 'True', 'to': "orm['auth.CustomUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_forked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'subtitles_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'newsubtitlelanguage_set'", 'to': "orm['videos.Video']"}),
            'writelock_owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'writelocked_newlanguages'", 'null': 'True', 'to': "orm['auth.CustomUser']"}),
            'writelock_session_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'writelock_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'subtitles.subtitleversion': {
            'Meta': {'unique_together': "[('video', 'subtitle_language', 'version_number'), ('video', 'language_code', 'version_number')]", 'object_name': 'SubtitleVersion'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'newsubtitleversion_set'", 'to': "orm['auth.CustomUser']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'meta_1_content': ('videos.metadata.MetadataContentField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'meta_2_content': ('videos.metadata.MetadataContentField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'meta_3_content': ('videos.metadata.MetadataContentField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '512', 'blank': 'True'}),
            'origin': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'parents': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['subtitles.SubtitleVersion']", 'symmetrical': 'False', 'blank': 'True'}),
            'rollback_of_version_number': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'serialized_lineage': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'serialized_subtitles': ('django.db.models.fields.TextField', [], {}),
            'subtitle_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'subtitle_language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subtitles.SubtitleLanguage']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'blank': 'True'}),
            'version_number': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'newsubtitleversion_set'", 'to': "orm['videos.Video']"}),
            'visibility': ('django.db.models.fields.CharField', [], {'default': "'public'", 'max_length': '10'}),
            'visibility_override': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'})
        },
        'teams.application': {
            'Meta': {'unique_together': "(('team', 'user', 'status'),)", 'object_name': 'Application'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'history': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'applications'", 'to': "orm['teams.Team']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'team_applications'", 'to': "orm['auth.CustomUser']"})
        },
        'teams.partner': {
            'Meta': {'object_name': 'Partner'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'managed_partners'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.CustomUser']"}),
            'can_request_paid_captions': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        'teams.project': {
            'Meta': {'unique_together': "(('team', 'name'), ('team', 'slug'))", 'object_name': 'Project'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'guidelines': ('django.db.models.fields.TextField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.Team']"}),
            'workflow_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'teams.team': {
            'Meta': {'ordering': "['name']", 'object_name': 'Team'},
            'applicants': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'applicated_teams'", 'symmetrical': 'False', 'through': "orm['teams.Application']", 'to': "orm['auth.CustomUser']"}),
            'application_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'auth_provider_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '24', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'header_html_text': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'highlight': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_moderated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_notification_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'logo': ('utils.amazon.fields.S3EnabledImageField', [], {'default': "''", 'max_length': '100', 'thumb_sizes': '[(280, 100), (100, 100)]', 'blank': 'True'}),
            'max_tasks_per_member': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'membership_policy': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
            'notify_interval': ('django.db.models.fields.CharField', [], {'default': "'D'", 'max_length': '1'}),
            'page_content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'partner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'teams'", 'null': 'True', 'to': "orm['teams.Partner']"}),
            'points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'projects_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'square_logo': ('utils.amazon.fields.S3EnabledImageField', [], {'default': "''", 'max_length': '100', 'thumb_sizes': '[(100, 100), (48, 48)]', 'blank': 'True'}),
            'subtitle_policy': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'sync_metadata': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task_assign_policy': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'task_expiration': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'translate_policy': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'teams'", 'symmetrical': 'False', 'through': "orm['teams.TeamMember']", 'to': "orm['auth.CustomUser']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'intro_for_teams'", 'null': 'True', 'to': "orm['videos.Video']"}),
            'video_policy': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'videos': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['videos.Video']", 'through': "orm['teams.TeamVideo']", 'symmetrical': 'False'}),
            'workflow_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'workflow_type': ('django.db.models.fields.CharField', [], {'default': "'O'", 'max_length': '2'})
        },
        'teams.teammember': {
            'Meta': {'unique_together': "(('team', 'user'),)", 'object_name': 'TeamMember'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'projects_managed': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'managers'", 'symmetrical': 'False', 'to': "orm['teams.Project']"}),
            'role': ('django.db.models.fields.CharField', [], {'default': "'contributor'", 'max_length': '16', 'db_index': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'members'", 'to': "orm['teams.Team']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'team_members'", 'to': "orm['auth.CustomUser']"})
        },
        'teams.teamvideo': {
            'Meta': {'unique_together': "(('team', 'video'),)", 'object_name': 'TeamVideo'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True'}),
            'all_languages': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'partner_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.Project']"}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.Team']"}),
            'thumbnail': ('utils.amazon.fields.S3EnabledImageField', [], {'max_length': '100', 'null': 'True', 'thumb_sizes': '((288, 162), (120, 90))', 'blank': 'True'}),
            'video': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['videos.Video']", 'unique': 'True'})
        },
        'videos.action': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Action'},
            'action_type': ('django.db.models.fields.IntegerField', [], {}),
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['comments.Comment']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleLanguage']", 'null': 'True', 'blank': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.TeamMember']", 'null': 'True', 'blank': 'True'}),
            'new_language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subtitles.SubtitleLanguage']", 'null': 'True', 'blank': 'True'}),
            'new_video_title': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.Team']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True', 'blank': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']", 'null': 'True', 'blank': 'True'})
        },
        'videos.importedvideo': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'ImportedVideo'},
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.VideoFeed']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'video': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['videos.Video']", 'unique': 'True'})
        },
        'videos.subtitle': {
            'Meta': {'ordering': "['subtitle_order']", 'unique_together': "(('version', 'subtitle_id'),)", 'object_name': 'Subtitle'},
            'end_time': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'db_column': "'end_time_ms'"}),
            'end_time_seconds': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_column': "'end_time'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_of_paragraph': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_time': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'db_column': "'start_time_ms'"}),
            'start_time_seconds': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_column': "'start_time'"}),
            'subtitle_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'subtitle_order': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'subtitle_text': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleVersion']", 'null': 'True'})
        },
        'videos.subtitlelanguage': {
            'Meta': {'unique_together': "(('video', 'language', 'standard_language'),)", 'object_name': 'SubtitleLanguage'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'followed_languages'", 'blank': 'True', 'to': "orm['auth.CustomUser']"}),
            'had_version': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_version': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_forked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_original': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'needs_sync': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'new_subtitle_language': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'old_subtitle_version'", 'null': 'True', 'to': "orm['subtitles.SubtitleLanguage']"}),
            'percent_done': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'standard_language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleLanguage']", 'null': 'True', 'blank': 'True'}),
            'subtitle_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"}),
            'writelock_owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True', 'blank': 'True'}),
            'writelock_session_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'writelock_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'videos.subtitlemetadata': {
            'Meta': {'ordering': "('created',)", 'object_name': 'SubtitleMetadata'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'subtitle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Subtitle']"})
        },
        'videos.subtitleversion': {
            'Meta': {'ordering': "['-version_no']", 'unique_together': "(('language', 'version_no'),)", 'object_name': 'SubtitleVersion'},
            'datetime_started': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'forked_from': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleVersion']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_forked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleLanguage']"}),
            'moderation_status': ('django.db.models.fields.CharField', [], {'default': "'not__under_moderation'", 'max_length': '32', 'db_index': 'True'}),
            'needs_sync': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'new_subtitle_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'old_subtitle_version'", 'unique': 'True', 'null': 'True', 'to': "orm['subtitles.SubtitleVersion']"}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'notification_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'result_of_rollback': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text_change': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'time_change': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']"}),
            'version_no': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'videos.subtitleversionmetadata': {
            'Meta': {'unique_together': "(('key', 'subtitle_version'),)", 'object_name': 'SubtitleVersionMetadata'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'subtitle_version': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metadata'", 'to': "orm['videos.SubtitleVersion']"})
        },
        'videos.usertestresult': {
            'Meta': {'object_name': 'UserTestResult'},
            'browser': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'get_updates': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task1': ('django.db.models.fields.TextField', [], {}),
            'task2': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'task3': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'videos.video': {
            'Meta': {'object_name': 'Video'},
            'allow_community_edits': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_video_urls_edit': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'complete_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'edited': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'featured': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'followed_videos'", 'blank': 'True', 'to': "orm['auth.CustomUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_subtitled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'languages_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'meta_1_content': ('videos.metadata.MetadataContentField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'meta_1_type': ('videos.metadata.MetadataTypeField', [], {'null': 'True', 'blank': 'True'}),
            'meta_2_content': ('videos.metadata.MetadataContentField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'meta_2_type': ('videos.metadata.MetadataTypeField', [], {'null': 'True', 'blank': 'True'}),
            'meta_3_content': ('videos.metadata.MetadataContentField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'meta_3_type': ('videos.metadata.MetadataTypeField', [], {'null': 'True', 'blank': 'True'}),
            'moderated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'moderating'", 'null': 'True', 'to': "orm['teams.Team']"}),
            'primary_audio_language_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'blank': 'True'}),
            's3_thumbnail': ('utils.amazon.fields.S3EnabledImageField', [], {'max_length': '100', 'thumb_sizes': '((480, 270), (288, 162), (120, 90))', 'blank': 'True'}),
            'small_thumbnail': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True', 'blank': 'True'}),
            'video_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'view_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'was_subtitled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'writelock_owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'writelock_owners'", 'null': 'True', 'to': "orm['auth.CustomUser']"}),
            'writelock_session_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'writelock_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'videos.videofeed': {
            'Meta': {'object_name': 'VideoFeed'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.Team']", 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True', 'blank': 'True'})
        },
        'videos.videoindex': {
            'Meta': {'object_name': 'VideoIndex'},
            'text': ('django.db.models.fields.TextField', [], {}),
            'video': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'index'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['videos.Video']"})
        },
        'videos.videometadata': {
            'Meta': {'ordering': "('created',)", 'object_name': 'VideoMetadata'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"})
        },
        'videos.videotypeurlpattern': {
            'Meta': {'object_name': 'VideoTypeUrlPattern'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'url_pattern': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '255'})
        },
        'videos.videourl': {
            'Meta': {'ordering': "('video', '-primary')", 'object_name': 'VideoUrl'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '512'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"}),
            'videoid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        }
    }

    complete_apps = ['videos']