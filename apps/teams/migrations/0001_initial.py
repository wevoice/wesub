# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Team'
        db.create_table('teams_team', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('logo', self.gf('utils.amazon.fields.S3EnabledImageField')(default='', max_length=100, thumb_sizes=[(280, 100), (100, 100)], blank=True)),
            ('square_logo', self.gf('utils.amazon.fields.S3EnabledImageField')(default='', max_length=100, thumb_sizes=[(100, 100), (48, 48)], blank=True)),
            ('is_visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('sync_metadata', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('points', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('highlight', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='intro_for_teams', null=True, to=orm['videos.Video'])),
            ('application_text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('page_content', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('is_moderated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('header_html_text', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('last_notification_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('notify_interval', self.gf('django.db.models.fields.CharField')(default='D', max_length=1)),
            ('auth_provider_code', self.gf('django.db.models.fields.CharField')(default='', max_length=24, blank=True)),
            ('workflow_type', self.gf('django.db.models.fields.CharField')(default='O', max_length=2)),
            ('projects_enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('workflow_enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('membership_policy', self.gf('django.db.models.fields.IntegerField')(default=4)),
            ('video_policy', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('task_assign_policy', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('subtitle_policy', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('translate_policy', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('max_tasks_per_member', self.gf('django.db.models.fields.PositiveIntegerField')(default=None, null=True, blank=True)),
            ('task_expiration', self.gf('django.db.models.fields.PositiveIntegerField')(default=None, null=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('partner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='teams', null=True, to=orm['teams.Partner'])),
        ))
        db.send_create_signal('teams', ['Team'])

        # Adding model 'Project'
        db.create_table('teams_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teams.Team'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=2048, null=True, blank=True)),
            ('guidelines', self.gf('django.db.models.fields.TextField')(max_length=2048, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('workflow_enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('teams', ['Project'])

        # Adding unique constraint on 'Project', fields ['team', 'name']
        db.create_unique('teams_project', ['team_id', 'name'])

        # Adding unique constraint on 'Project', fields ['team', 'slug']
        db.create_unique('teams_project', ['team_id', 'slug'])

        # Adding model 'TeamVideo'
        db.create_table('teams_teamvideo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teams.Team'])),
            ('video', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['videos.Video'], unique=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('thumbnail', self.gf('utils.amazon.fields.S3EnabledImageField')(max_length=100, null=True, thumb_sizes=((288, 162), (120, 90)), blank=True)),
            ('all_languages', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('added_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.CustomUser'], null=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('partner_id', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teams.Project'])),
        ))
        db.send_create_signal('teams', ['TeamVideo'])

        # Adding unique constraint on 'TeamVideo', fields ['team', 'video']
        db.create_unique('teams_teamvideo', ['team_id', 'video_id'])

        # Adding model 'TeamVideoMigration'
        db.create_table('teams_teamvideomigration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_team', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['teams.Team'])),
            ('to_team', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['teams.Team'])),
            ('to_project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['teams.Project'])),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('teams', ['TeamVideoMigration'])

        # Adding model 'TeamMember'
        db.create_table('teams_teammember', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(related_name='members', to=orm['teams.Team'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='team_members', to=orm['auth.CustomUser'])),
            ('role', self.gf('django.db.models.fields.CharField')(default='contributor', max_length=16, db_index=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
        ))
        db.send_create_signal('teams', ['TeamMember'])

        # Adding unique constraint on 'TeamMember', fields ['team', 'user']
        db.create_unique('teams_teammember', ['team_id', 'user_id'])

        # Adding M2M table for field projects_managed on 'TeamMember'
        db.create_table('teams_teammember_projects_managed', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('teammember', models.ForeignKey(orm['teams.teammember'], null=False)),
            ('project', models.ForeignKey(orm['teams.project'], null=False))
        ))
        db.create_unique('teams_teammember_projects_managed', ['teammember_id', 'project_id'])

        # Adding model 'LanguageManager'
        db.create_table('teams_languagemanager', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages_managed', to=orm['teams.TeamMember'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('teams', ['LanguageManager'])

        # Adding model 'MembershipNarrowing'
        db.create_table('teams_membershipnarrowing', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(related_name='narrowings', to=orm['teams.TeamMember'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teams.Project'], null=True, blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=24, blank=True)),
            ('added_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='narrowing_includer', null=True, to=orm['teams.TeamMember'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('teams', ['MembershipNarrowing'])

        # Adding model 'TeamSubtitleNote'
        db.create_table('teams_teamsubtitlenote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['videos.Video'])),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.CustomUser'])),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['teams.Team'])),
        ))
        db.send_create_signal('teams', ['TeamSubtitleNote'])

        # Adding model 'Application'
        db.create_table('teams_application', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(related_name='applications', to=orm['teams.Team'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='team_applications', to=orm['auth.CustomUser'])),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('status', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('history', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('teams', ['Application'])

        # Adding unique constraint on 'Application', fields ['team', 'user', 'status']
        db.create_unique('teams_application', ['team_id', 'user_id', 'status'])

        # Adding model 'Invite'
        db.create_table('teams_invite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invitations', to=orm['teams.Team'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='team_invitations', to=orm['auth.CustomUser'])),
            ('note', self.gf('django.db.models.fields.TextField')(max_length=200, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.CustomUser'])),
            ('role', self.gf('django.db.models.fields.CharField')(default='contributor', max_length=16)),
            ('approved', self.gf('django.db.models.fields.NullBooleanField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal('teams', ['Invite'])

        # Adding model 'Workflow'
        db.create_table('teams_workflow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teams.Team'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teams.Project'], null=True, blank=True)),
            ('team_video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teams.TeamVideo'], null=True, blank=True)),
            ('autocreate_subtitle', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('autocreate_translate', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('review_allowed', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('approve_allowed', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('teams', ['Workflow'])

        # Adding unique constraint on 'Workflow', fields ['team', 'project', 'team_video']
        db.create_unique('teams_workflow', ['team_id', 'project_id', 'team_video_id'])

        # Adding model 'Task'
        db.create_table('teams_task', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teams.Team'])),
            ('team_video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teams.TeamVideo'])),
            ('language', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=16, blank=True)),
            ('assignee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.CustomUser'], null=True, blank=True)),
            ('subtitle_version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.SubtitleVersion'], null=True, blank=True)),
            ('new_subtitle_version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subtitles.SubtitleVersion'], null=True, blank=True)),
            ('review_base_version', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tasks_based_on', null=True, to=orm['videos.SubtitleVersion'])),
            ('new_review_base_version', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tasks_based_on_new', null=True, to=orm['subtitles.SubtitleVersion'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('completed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('expiration_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True, blank=True)),
            ('approved', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('teams', ['Task'])

        # Adding model 'Setting'
        db.create_table('teams_setting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('data', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(related_name='settings', to=orm['teams.Team'])),
            ('language_code', self.gf('django.db.models.fields.CharField')(default='', max_length=16, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('teams', ['Setting'])

        # Adding unique constraint on 'Setting', fields ['key', 'team', 'language_code']
        db.create_unique('teams_setting', ['key', 'team_id', 'language_code'])

        # Adding model 'TeamLanguagePreference'
        db.create_table('teams_teamlanguagepreference', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(related_name='lang_preferences', to=orm['teams.Team'])),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('allow_reads', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_writes', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('preferred', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('teams', ['TeamLanguagePreference'])

        # Adding unique constraint on 'TeamLanguagePreference', fields ['team', 'language_code']
        db.create_unique('teams_teamlanguagepreference', ['team_id', 'language_code'])

        # Adding model 'TeamNotificationSetting'
        db.create_table('teams_teamnotificationsetting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='notification_settings', unique=True, null=True, to=orm['teams.Team'])),
            ('partner', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='notification_settings', unique=True, null=True, to=orm['teams.Partner'])),
            ('request_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('basic_auth_username', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('basic_auth_password', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('notification_class', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('teams', ['TeamNotificationSetting'])

        # Adding model 'BillingReport'
        db.create_table('teams_billingreport', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('csv_file', self.gf('utils.amazon.fields.S3EnabledFileField')(max_length=100, null=True, blank=True)),
            ('processed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(default=2)),
        ))
        db.send_create_signal('teams', ['BillingReport'])

        # Adding M2M table for field teams on 'BillingReport'
        db.create_table('teams_billingreport_teams', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('billingreport', models.ForeignKey(orm['teams.billingreport'], null=False)),
            ('team', models.ForeignKey(orm['teams.team'], null=False))
        ))
        db.create_unique('teams_billingreport_teams', ['billingreport_id', 'team_id'])

        # Adding model 'BillingRecord'
        db.create_table('teams_billingrecord', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.Video'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teams.Project'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('subtitle_version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.SubtitleVersion'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('new_subtitle_version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subtitles.SubtitleVersion'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('subtitle_language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.SubtitleLanguage'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('new_subtitle_language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subtitles.SubtitleLanguage'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('minutes', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('is_original', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teams.Team'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.CustomUser'])),
        ))
        db.send_create_signal('teams', ['BillingRecord'])

        # Adding unique constraint on 'BillingRecord', fields ['video', 'new_subtitle_language']
        db.create_unique('teams_billingrecord', ['video_id', 'new_subtitle_language_id'])

        # Adding model 'Partner'
        db.create_table('teams_partner', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('can_request_paid_captions', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('teams', ['Partner'])

        # Adding M2M table for field admins on 'Partner'
        db.create_table('teams_partner_admins', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('partner', models.ForeignKey(orm['teams.partner'], null=False)),
            ('customuser', models.ForeignKey(orm['auth.customuser'], null=False))
        ))
        db.create_unique('teams_partner_admins', ['partner_id', 'customuser_id'])

    def backwards(self, orm):
        # Removing unique constraint on 'BillingRecord', fields ['video', 'new_subtitle_language']
        db.delete_unique('teams_billingrecord', ['video_id', 'new_subtitle_language_id'])

        # Removing unique constraint on 'TeamLanguagePreference', fields ['team', 'language_code']
        db.delete_unique('teams_teamlanguagepreference', ['team_id', 'language_code'])

        # Removing unique constraint on 'Setting', fields ['key', 'team', 'language_code']
        db.delete_unique('teams_setting', ['key', 'team_id', 'language_code'])

        # Removing unique constraint on 'Workflow', fields ['team', 'project', 'team_video']
        db.delete_unique('teams_workflow', ['team_id', 'project_id', 'team_video_id'])

        # Removing unique constraint on 'Application', fields ['team', 'user', 'status']
        db.delete_unique('teams_application', ['team_id', 'user_id', 'status'])

        # Removing unique constraint on 'TeamMember', fields ['team', 'user']
        db.delete_unique('teams_teammember', ['team_id', 'user_id'])

        # Removing unique constraint on 'TeamVideo', fields ['team', 'video']
        db.delete_unique('teams_teamvideo', ['team_id', 'video_id'])

        # Removing unique constraint on 'Project', fields ['team', 'slug']
        db.delete_unique('teams_project', ['team_id', 'slug'])

        # Removing unique constraint on 'Project', fields ['team', 'name']
        db.delete_unique('teams_project', ['team_id', 'name'])

        # Deleting model 'Team'
        db.delete_table('teams_team')

        # Deleting model 'Project'
        db.delete_table('teams_project')

        # Deleting model 'TeamVideo'
        db.delete_table('teams_teamvideo')

        # Deleting model 'TeamVideoMigration'
        db.delete_table('teams_teamvideomigration')

        # Deleting model 'TeamMember'
        db.delete_table('teams_teammember')

        # Removing M2M table for field projects_managed on 'TeamMember'
        db.delete_table('teams_teammember_projects_managed')

        # Deleting model 'LanguageManager'
        db.delete_table('teams_languagemanager')

        # Deleting model 'MembershipNarrowing'
        db.delete_table('teams_membershipnarrowing')

        # Deleting model 'TeamSubtitleNote'
        db.delete_table('teams_teamsubtitlenote')

        # Deleting model 'Application'
        db.delete_table('teams_application')

        # Deleting model 'Invite'
        db.delete_table('teams_invite')

        # Deleting model 'Workflow'
        db.delete_table('teams_workflow')

        # Deleting model 'Task'
        db.delete_table('teams_task')

        # Deleting model 'Setting'
        db.delete_table('teams_setting')

        # Deleting model 'TeamLanguagePreference'
        db.delete_table('teams_teamlanguagepreference')

        # Deleting model 'TeamNotificationSetting'
        db.delete_table('teams_teamnotificationsetting')

        # Deleting model 'BillingReport'
        db.delete_table('teams_billingreport')

        # Removing M2M table for field teams on 'BillingReport'
        db.delete_table('teams_billingreport_teams')

        # Deleting model 'BillingRecord'
        db.delete_table('teams_billingrecord')

        # Deleting model 'Partner'
        db.delete_table('teams_partner')

        # Removing M2M table for field admins on 'Partner'
        db.delete_table('teams_partner_admins')

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
        'teams.billingrecord': {
            'Meta': {'unique_together': "(('video', 'new_subtitle_language'),)", 'object_name': 'BillingRecord'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_original': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'minutes': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'new_subtitle_language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subtitles.SubtitleLanguage']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'new_subtitle_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subtitles.SubtitleVersion']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.Project']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subtitle_language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleLanguage']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'subtitle_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleVersion']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.Team']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'teams.billingreport': {
            'Meta': {'object_name': 'BillingReport'},
            'csv_file': ('utils.amazon.fields.S3EnabledFileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'teams': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'billing_reports'", 'symmetrical': 'False', 'to': "orm['teams.Team']"}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '2'})
        },
        'teams.invite': {
            'Meta': {'object_name': 'Invite'},
            'approved': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'max_length': '200', 'blank': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'default': "'contributor'", 'max_length': '16'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invitations'", 'to': "orm['teams.Team']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'team_invitations'", 'to': "orm['auth.CustomUser']"})
        },
        'teams.languagemanager': {
            'Meta': {'object_name': 'LanguageManager'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages_managed'", 'to': "orm['teams.TeamMember']"})
        },
        'teams.membershipnarrowing': {
            'Meta': {'object_name': 'MembershipNarrowing'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'narrowing_includer'", 'null': 'True', 'to': "orm['teams.TeamMember']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '24', 'blank': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'narrowings'", 'to': "orm['teams.TeamMember']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.Project']", 'null': 'True', 'blank': 'True'})
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
        'teams.setting': {
            'Meta': {'unique_together': "(('key', 'team', 'language_code'),)", 'object_name': 'Setting'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'language_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'settings'", 'to': "orm['teams.Team']"})
        },
        'teams.task': {
            'Meta': {'object_name': 'Task'},
            'approved': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True', 'blank': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'expiration_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '16', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'new_review_base_version': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tasks_based_on_new'", 'null': 'True', 'to': "orm['subtitles.SubtitleVersion']"}),
            'new_subtitle_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subtitles.SubtitleVersion']", 'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'review_base_version': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tasks_based_on'", 'null': 'True', 'to': "orm['videos.SubtitleVersion']"}),
            'subtitle_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleVersion']", 'null': 'True', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.Team']"}),
            'team_video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.TeamVideo']"}),
            'type': ('django.db.models.fields.PositiveIntegerField', [], {})
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
        'teams.teamlanguagepreference': {
            'Meta': {'unique_together': "(('team', 'language_code'),)", 'object_name': 'TeamLanguagePreference'},
            'allow_reads': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_writes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'preferred': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lang_preferences'", 'to': "orm['teams.Team']"})
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
        'teams.teamnotificationsetting': {
            'Meta': {'object_name': 'TeamNotificationSetting'},
            'basic_auth_password': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'basic_auth_username': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notification_class': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'partner': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'notification_settings'", 'unique': 'True', 'null': 'True', 'to': "orm['teams.Partner']"}),
            'request_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'notification_settings'", 'unique': 'True', 'null': 'True', 'to': "orm['teams.Team']"})
        },
        'teams.teamsubtitlenote': {
            'Meta': {'object_name': 'TeamSubtitleNote'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['teams.Team']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.CustomUser']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['videos.Video']"})
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
        'teams.teamvideomigration': {
            'Meta': {'object_name': 'TeamVideoMigration'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'from_team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['teams.Team']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['teams.Project']"}),
            'to_team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['teams.Team']"})
        },
        'teams.workflow': {
            'Meta': {'unique_together': "(('team', 'project', 'team_video'),)", 'object_name': 'Workflow'},
            'approve_allowed': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'autocreate_subtitle': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'autocreate_translate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.Project']", 'null': 'True', 'blank': 'True'}),
            'review_allowed': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.Team']"}),
            'team_video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.TeamVideo']", 'null': 'True', 'blank': 'True'})
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
        }
    }

    complete_apps = ['teams']