# Universal Subtitles, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.
import logging
from datetime import datetime

from django.conf import settings
from django.db.models import Sum, Q
from django.utils import translation
from django.utils.translation import ugettext as _

from icanhaz.models import VideoVisibilityPolicy
from statistic.tasks import st_widget_view_statistic_update
from teams.models import Task, Workflow
from teams.moderation_const import UNMODERATED, WAITING_MODERATION
from teams.permissions import (
    can_create_and_edit_subtitles, can_create_and_edit_translations,
    can_publish_edits_immediately, can_review, can_approve
)
from teams.signals import (
    api_subtitles_edited, api_subtitles_approved, api_subtitles_rejected,
    api_language_new, api_language_edited, api_video_edited
)
from uslogging.models import WidgetDialogLog
from utils import send_templated_email
from utils.forms import flatten_errorlists
from utils.translation import get_user_languages_from_request
from videos import models
from videos.tasks import video_changed_tasks
from widget import video_cache
from widget.base_rpc import BaseRpc
from widget.forms import  FinishReviewForm, FinishApproveForm
from widget.models import SubtitlingSession


yt_logger = logging.getLogger("youtube-ei-error")

ALL_LANGUAGES = settings.ALL_LANGUAGES
LANGUAGES_MAP = dict(ALL_LANGUAGES)

def add_general_settings(request, dict):
    dict.update({
            'writelock_expiration' : models.WRITELOCK_EXPIRATION,
            'embed_version': settings.EMBED_JS_VERSION,
            'languages': ALL_LANGUAGES,
            'metadata_languages': settings.METADATA_LANGUAGES
            })
    if request.user.is_authenticated():
        dict['username'] = request.user.username

class Rpc(BaseRpc):
    def log_session(self, request,  log):
        dialog_log = WidgetDialogLog(
            browser_id=request.browser_id,
            log=log)
        dialog_log.save()
        send_templated_email(
            settings.WIDGET_LOG_EMAIL,
            'Subtitle save failure',
            'widget/session_log_email.txt',
            { 'log_pk': dialog_log.pk },
            fail_silently=False)
        return { 'response': 'ok' }

    def log_youtube_ei_failure(self, request, page_url):
        user_agent = request.META.get('HTTP_USER_AGENT', '(Unknown)')
        yt_logger.error(
            "Youtube ExternalInterface load failure",
            extra={
                'request': request,
                'data': {
                    'user_agent': user_agent,
                    'page_url': page_url }
                })
        return { 'response': 'ok' }

    def show_widget(self, request, video_url, is_remote, base_state=None, additional_video_urls=None):
        try:
            video_id = video_cache.get_video_id(video_url)
        except Exception as e:
            # for example, private youtube video or private widgets
            return {"error_msg": unicode(e)}

        if video_id is None:
            return None
        visibility_policy = video_cache.get_visibility_policies(video_id)
        if visibility_policy.get('widget', None) != VideoVisibilityPolicy.WIDGET_VISIBILITY_PUBLIC:
            if not VideoVisibilityPolicy.objects.can_show_widget(
                video_id,
                referer=request.META.get('referer'),
                user=request.user):
                return {"error_msg": _("Video embedding disabled by owner")}
        try:
            video_urls = video_cache.get_video_urls(video_id)
        except models.Video.DoesNotExist:
            video_cache.invalidate_video_id(video_url)
            try:
                video_id = video_cache.get_video_id(video_url)
            except Exception as e:
                return {"error_msg": unicode(e)}
            video_urls = video_cache.get_video_urls(video_id)

        return_value = {
            'video_id' : video_id,
            'subtitles': None,
        }
        return_value['video_urls']= video_urls
        return_value['is_moderated'] = video_cache.get_is_moderated(video_id)
        if additional_video_urls is not None:
            for url in additional_video_urls:
                video_cache.associate_extra_url(url, video_id)

        add_general_settings(request, return_value)
        if request.user.is_authenticated():
            return_value['username'] = request.user.username

        return_value['drop_down_contents'] = \
            video_cache.get_video_languages(video_id)

        return_value['my_languages'] = \
            get_user_languages_from_request(request)

        # keeping both forms valid as backwards compatibility layer
        lang_code = base_state and base_state.get("language_code", base_state.get("language", None))
        if base_state is not None and lang_code is not None:
            lang_pk = base_state.get('language_pk', None)
            if lang_pk is  None:
                lang_pk = video_cache.pk_for_default_language(video_id, lang_code)
            subtitles = self._autoplay_subtitles(
                request.user, video_id,
                lang_pk,
                base_state.get('revision', None))
            return_value['subtitles'] = subtitles
        else:
            if is_remote:
                autoplay_language = self._find_remote_autoplay_language(request)
                language_pk = video_cache.pk_for_default_language(video_id, autoplay_language)
                if autoplay_language is not None:
                    subtitles = self._autoplay_subtitles(
                        request.user, video_id, language_pk, None)
                    return_value['subtitles'] = subtitles

        return return_value

    def track_subtitle_play(self, request, video_id):
        st_widget_view_statistic_update.delay(video_id=video_id)
        return { 'response': 'ok' }

    def _find_remote_autoplay_language(self, request):
        language = None
        if not request.user.is_authenticated() or request.user.preferred_language == '':
            language = translation.get_language_from_request(request)
        else:
            language = request.user.preferred_language
        return language if language != '' else None

    def fetch_start_dialog_contents(self, request, video_id):
        my_languages = get_user_languages_from_request(request)
        my_languages.extend([l[:l.find('-')] for l in my_languages if l.find('-') > -1])
        video = models.Video.objects.get(video_id=video_id)
        team_video = video.get_team_video()
        video_languages = [language_summary(l, team_video, request.user) for l
                           in video.subtitlelanguage_set.all()]

        original_language = None
        if video.subtitle_language():
            original_language = video.subtitle_language().language

        tv = video.get_team_video()
        writable_langs = list(tv.team.get_writable_langs()) if tv else []

        return {
            'my_languages': my_languages,
            'video_languages': video_languages,
            'original_language': original_language,
            'limit_languages': writable_langs,
            'is_moderated': video.is_moderated, }

    def fetch_video_id_and_settings(self, request, video_id):
        is_original_language_subtitled = self._subtitle_count(video_id) > 0
        general_settings = {}
        add_general_settings(request, general_settings)
        return {
            'video_id': video_id,
            'is_original_language_subtitled': is_original_language_subtitled,
            'general_settings': general_settings }


    def _check_team_video_locking(self, user, video_id, language_code, is_translation, mode, is_edit):
        """Check whether the a team prevents the user from editing the subs.

        Returns a dict appropriate for sending back if the user should be
        prevented from editing them, or None if the user can safely edit.

        """
        video = models.Video.objects.get(video_id=video_id)
        team_video = video.get_team_video()

        if not team_video:
            # If there's no team video to worry about, just bail early.
            return None

        # Check that there are no open tasks for this action.
        tasks = team_video.task_set.incomplete().filter(language=language_code)
        if tasks:
            task = tasks[0]
            if not user.is_authenticated() or user != task.assignee:
                return { "can_edit": False, "locked_by": str(task.assignee or task.team) }

        # Check that the team's policies don't prevent the action.
        if not is_edit and mode not in ['review', 'approve']:
            if is_translation:
                can_edit = can_create_and_edit_translations(user, team_video, language_code)
            else:
                can_edit = can_create_and_edit_subtitles(user, team_video, language_code)

            if not can_edit:
                return { "can_edit": False, "locked_by": str(team_video.team) }

    def start_editing(self, request, video_id, language_code,
                      subtitle_language_pk=None, base_language_pk=None,
                      original_language_code=None, mode=None):
        """Called by subtitling widget when subtitling or translation is to commence on a video.

        Does a lot of things, some of which should probably be split out into
        other functions.

        """
        # TODO: remove whenever blank SubtitleLanguages become illegal.
        self._fix_blank_original(video_id)
        if language_code == original_language_code:
            base_language_pk = None
        base_language = None
        if base_language_pk is not None:
            base_language = models.SubtitleLanguage.objects.get(
                pk=base_language_pk)

        language, can_edit = self._get_language_for_editing(
            request, video_id, language_code,
            subtitle_language_pk, base_language)

        if not can_edit:
            return { "can_edit": False,
                     "locked_by" : language.writelock_owner_name }

        session = self._make_subtitling_session(
            request, language, base_language)

        version_for_subs = language.version(public_only=False)

        if not version_for_subs:
            version_for_subs = self._create_version_from_session(session)
            version_no = 0
            is_edit = False
        else:
            version_no = version_for_subs.version_no + 1
            is_edit = True

        locked = self._check_team_video_locking(request.user, video_id,
                        language_code, bool(base_language_pk), mode, is_edit)
        if locked:
            return locked

        subtitles = self._subtitles_dict(
            version_for_subs, version_no, base_language_pk is None)
        return_dict = { "can_edit" : True,
                        "session_pk" : session.pk,
                        "subtitles" : subtitles }
        if base_language:
            return_dict['original_subtitles'] = \
                self._subtitles_dict(base_language.latest_version())
        if original_language_code:
            self._save_original_language(video_id, original_language_code)
        video_cache.writelock_add_lang(video_id, language.language)
        return return_dict


    def resume_editing(self, request, session_pk):
        session = SubtitlingSession.objects.get(pk=session_pk)
        if session.language.can_writelock(request) and \
                session.parent_version == session.language.version():
            session.language.writelock(request)
            # FIXME: Duplication between this and start_editing.
            version_for_subs = session.language.version()
            if not version_for_subs:
                version_for_subs = self._create_version_from_session(session)
                version_no = 0
            else:
                version_no = version_for_subs.version_no + 1
            subtitles = self._subtitles_dict(version_for_subs, version_no)
            return_dict = { "response": "ok",
                            "can_edit" : True,
                            "session_pk" : session.pk,
                            "subtitles" : subtitles }
            if session.base_language:
                return_dict['original_subtitles'] = \
                    self._subtitles_dict(session.base_language.latest_version())
            return return_dict
        else:
            return { 'response': 'cannot_resume' }

    def release_lock(self, request, session_pk):
        language = SubtitlingSession.objects.get(pk=session_pk).language
        if language.can_writelock(request):
            language.release_writelock()
            language.save()
            video_cache.writelocked_langs_clear(language.video.video_id)
        return { "response": "ok" }

    def regain_lock(self, request, session_pk):
        language = SubtitlingSession.objects.get(pk=session_pk).language
        if not language.can_writelock(request):
            return { 'response': 'unlockable' }
        else:
            language.writelock(request)
            language.save()
            video_cache.writelock_add_lang(
                language.video.video_id, language.language)
            return { 'response': 'ok' }


    def can_user_edit_video(self, request, video_id):
        """Return a dictionary of information about what the user can do with this video.

        The response will contain can_subtitle and can_translate attributes.

        """
        video = models.Video.objects.get(video_id=video_id)
        team_video = video.get_team_video()

        if not team_video:
            return {'response': 'ok', 'can_subtitle': True, 'can_translate': True}
        else:
            return {'response': 'ok',
                    'can_subtitle': can_create_and_edit_subtitles(request.user, team_video),
                    'can_translate': can_create_and_edit_translations(request.user, team_video)}


    def finished_subtitles(self, request, session_pk, subtitles=None,
                           new_title=None, completed=None,
                           forked=False,
                           throw_exception=False, new_description=None,
                           task_id=None, task_notes=None, task_approved=None, task_type=None):
        session = SubtitlingSession.objects.get(pk=session_pk)
        if not request.user.is_authenticated():
            return { 'response': 'not_logged_in' }
        if not session.language.can_writelock(request):
            return { "response" : "unlockable" }
        if not session.matches_request(request):
            return { "response" : "does not match request" }

        if throw_exception:
            raise Exception('purposeful exception for testing')

        return self.save_finished(
            request, request.user, session, subtitles, new_title, completed,
            forked, new_description, task_id, task_notes, task_approved, task_type)

    def save_finished(self, request, user, session, subtitles, new_title=None,
                      completed=None, forked=False, new_description=None,
                      task_id=None, task_notes=None, task_approved=None, task_type=None):
        # TODO: lock all this in a transaction please!
        language = session.language
        # if this belongs to a task finish it:

        new_version = None
        if subtitles is not None and \
                (len(subtitles) > 0 or language.latest_version(public_only=False) is not None):
            new_version = self._create_version_from_session(session, user, forked)
            new_version.save()

            if hasattr(new_version, 'task_to_save'):
                new_version.task_to_save.subtitle_version = new_version
                new_version.task_to_save.save()

            self._save_subtitles(
                new_version.subtitle_set, subtitles, new_version.is_forked)

        # if any of the language attributes have changed (title, descr,
        # completedness) we must trigger the api notification.
        must_trigger_api_language_edited = False
        language.release_writelock()
        if completed is not None:
            language.is_complete = completed
            if language.is_complete != completed:
                must_trigger_api_language_edited = True
        if new_title is not None:
            language.title = new_title
            if language.is_original:
                language.video.title = language.title
            must_trigger_api_language_edited = True
        if new_description is not None:
            language.description = new_description
            if language.is_original:
                language.video.description = language.description
            must_trigger_api_language_edited = True
        language.save()

        if must_trigger_api_language_edited:
            language.video.save()
            api_language_edited.send(language)

        if new_version is not None:
            video_changed_tasks.delay(language.video.id, new_version.id)
            api_subtitles_edited.send(new_version)
        else:
            video_changed_tasks.delay(language.video.id)
            api_video_edited.send(language.video)

        # The message displayed to the user  has a complex requirement /  outcomes
        # 1) Subs will go live in a moment. Works for unmoderated subs and for D and H
        # D. Transcript, post-publish edit by moderator with the power to approve. Will go live immediately.
        # H. Translation, post-publish edit by moderator with the power to approve. Will go live immediately.
        # 2) Subs must be completed before being submitted to moderators. Works for A and E
        # A. Transcript, incomplete (checkbox not ticked). Must be completed before being submitted to moderators.
        # E. Translation, incomplete (some lines missing). Must be completed before being submitted to moderators.
        # 3) Subs will be submitted for review/approval. Works for B, C, F, and G
        # B. Transcript, complete (checkbox ticked). Will be submitted to moderators promptly for approval or rejection.
        # C. Transcript, post-publish edit by contributor. Will be submitted to moderators promptly for approval or rejection.
        # F. Translation, complete (all the lines filled). Will be submitted to moderators promptly for approval or rejection.
        # G. Translation, post-publish edit by contributor. Will be submitted to moderators promptly for approval or rejection.
        message_will_be_live_soon = "Your changes have been saved. It may take a moment for your subtitles to appear."
        message_will_be_submited = ("This video is moderated by %s."
                                    "Your changes will be reviewed by the "
                                    "team's moderators.")
        message_incomplete = ("These subtitles are incomplete. "
                              "They will not be submitted for publishing "
                              "until they've been completed.")
        under_moderation = language.video.is_moderated

        _user_can_publish =  True
        team_video_set = language.video.teamvideo_set
        if under_moderation and team_video_set.exists():
            # videos are only supposed to have one team video
            _user_can_publish = can_publish_edits_immediately(team_video_set.all()[0], user, language.language)
        is_complete = language.is_complete or language.calculate_percent_done() == 100
        # this is case 1
        if under_moderation and _user_can_publish is False:
            if is_complete:
                # case 3
                user_message = message_will_be_submited % ( language.video.moderated_by.name)
            else:
                # case 2
                user_message = message_incomplete
        else:
            user_message = message_will_be_live_soon

        # If we've just saved a completed subtitle language, we may need to
        # complete a subtitle or translation task.
        if is_complete:
            team_video = language.video.get_team_video()
            if team_video:
                tasks = team_video.task_set.incomplete().filter(
                    type__in=(Task.TYPE_IDS['Subtitle'],
                              Task.TYPE_IDS['Translate']),
                    language=language.language
                )
                for task in tasks:
                    task.complete()
        if task_id:
            res = {
                "review": self._finish_review,
                "approve": self._finish_approve
            }[task_type](request, task_id, task_notes, task_approved,
                         new_version=new_version)
            # if the task did not succeeded, just bail out
            if not res.get('response', 'ok'):
                return res

        return {
            'user_message': user_message,
            'response': 'ok' }

    def _save_subtitles(self, subtitle_set, json_subs, forked):
        for s in json_subs:
            if not forked:
                subtitle_set.create(
                    subtitle_id=s['subtitle_id'],
                    subtitle_text=s['text'])
            else:
                subtitle_set.create(
                    subtitle_id=s['subtitle_id'],
                    subtitle_text=s['text'],
                    start_time=s['start_time'],
                    end_time=s['end_time'],
                    subtitle_order=s['sub_order'],
                    start_of_paragraph=s.get('start_of_paragraph', False),
                )


    def _get_review_or_approve_task(self, team_video, subtitle_language):
        lang = subtitle_language.language
        workflow = Workflow.get_for_team_video(team_video)

        if workflow.approve_allowed:
            type = Task.TYPE_IDS['Approve']
            can_do = can_approve
        elif workflow.review_allowed:
            type = Task.TYPE_IDS['Review']
            can_do = can_review
        else:
            return None

        # TODO: Dedupe this and Task._find_previous_assignee

        # Find the assignee.
        #
        # For now, we'll assign the review/approval task to whomever did
        # it last time (if it was indeed done), but only if they're
        # still eligible to perform it now.
        last_task = team_video.task_set.complete().filter(
            language=lang, type=type
        ).order_by('-completed')[:1]

        assignee = None
        if last_task:
            candidate = last_task[0].assignee
            if candidate and can_do(team_video, candidate, lang):
                assignee = candidate

        # This is just terrible.
        #
        # We have to create a task here, but we need to have the
        # subtitle_version to do it correctly, and that doesn't get
        # saved until much later, a few functions away.
        return Task(team=team_video.team, team_video=team_video,
                    assignee=assignee, language=lang, type=type)

    def _moderate_session(self, session, user):
        """Return the right moderation_status for a version based on the given session.

        Also may possibly return a Task object that needs to be saved once the
        subtitle_version is ready.

        Also perform any ancillary tasks that are appropriate, assuming the
        version actually gets created later.

        Also :(

        """
        sl = session.language
        team_video = sl.video.get_team_video()

        if not team_video:
            return UNMODERATED, None

        # If there are any open team tasks for this video/language, it needs to
        # be kept under moderation.
        tasks = team_video.task_set.incomplete().filter(
                Q(language=sl.language)
              | Q(type=Task.TYPE_IDS['Subtitle'])
        )
        if tasks:
            for task in tasks:
                if task.type == Task.TYPE_IDS['Subtitle']:
                    if not task.language:
                        task.language = sl.language
                        task.save()
            return WAITING_MODERATION, None

        if sl.has_version:
            # If there are already active subtitles for this language, we're
            # dealing with an edit.
            if not can_publish_edits_immediately(team_video, user, sl.language):
                task = self._get_review_or_approve_task(team_video, sl)
                if task:
                    return WAITING_MODERATION, task
        else:
            # Otherwise we're dealing with a new set of subtitles for this
            # language.
            task = self._get_review_or_approve_task(team_video, sl)
            if task:
                return WAITING_MODERATION, task

        return UNMODERATED, None

    def _create_version_from_session(self, session, user=None, forked=False):
        latest_version = session.language.version(public_only=False)
        forked_from = (forked and latest_version) or None

        moderation_status, task = self._moderate_session(session, user)

        kwargs = dict(language=session.language,
                      version_no=(0 if latest_version is None
                                  else latest_version.version_no + 1),
                      is_forked=(session.base_language is
                                 None or forked == True),
                      forked_from=forked_from,
                      datetime_started=session.datetime_started,
                      moderation_status=moderation_status)

        if user is not None:
            kwargs['user'] = user

        version = models.SubtitleVersion(**kwargs)

        if task:
            # We may have a task that needs to be saved *after* this version is
            # saved.
            version.task_to_save = task

        return version

    def fetch_subtitles(self, request, video_id, language_pk):
        cache = video_cache.get_subtitles_dict(
            video_id, language_pk, None,
            lambda version: self._subtitles_dict(version))
        return cache

    def get_widget_info(self, request):
        return {
            'all_videos': models.Video.objects.count(),
            'subtitles_fetched_count': models.Video.objects.aggregate(s=Sum('subtitles_fetched_count'))['s'],
            'videos_with_captions': models.Video.objects.exclude(subtitlelanguage=None).count(),
            'translations_count': models.SubtitleLanguage.objects.filter(is_original=False).count()
        }

    def _make_subtitling_session(self, request, language, base_language):
        session = SubtitlingSession(
            language=language,
            base_language=base_language,
            parent_version=language.version(),
            browser_id=request.browser_id)
        if request.user.is_authenticated():
            session.user = request.user
        session.save()
        return session


    def fetch_review_data(self, request, task_id):
        task = Task.objects.get(pk=task_id)
        return {'response': 'ok', 'body': task.body}

    def _finish_review(self, request, task_id=None, body=None,
                       approved=None, new_version=None):
        """
        If the task performer has edited this version, then we need to
        set the task's version to the new one that he has edited.
        """
        data = {'task': task_id, 'body': body, 'approved': approved}

        form = FinishReviewForm(request, data)

        if form.is_valid():
            task = form.cleaned_data['task']
            task.body = form.cleaned_data['body']
            task.approved = form.cleaned_data['approved']
            # if there is a new version, set that as the tasks's one
            if new_version:
                task.subtitle_version = new_version
            task.save()

            if task.approved in Task.APPROVED_FINISHED_IDS:
                task.complete()

            task.subtitle_version.language.release_writelock()
            task.subtitle_version.language.followers.add(request.user)

            if form.cleaned_data['approved'] == Task.APPROVED_IDS['Approved']:
                user_message =  'These subtitles have been accepted and your notes have been sent to the author.'
            elif form.cleaned_data['approved'] == Task.APPROVED_IDS['Rejected']:
                user_message =  'These subtitles have been rejected and your notes have been sent to the author.'
            else:
                user_message =  'Your notes have been saved.'

            video_changed_tasks.delay(task.team_video.video_id)
            return {'response': 'ok', 'user_message': user_message}
        else:
            return {'error_msg': _(u'\n'.join(flatten_errorlists(form.errors)))}


    def fetch_approve_data(self, request, task_id):
        task = Task.objects.get(pk=task_id)
        return {'response': 'ok', 'body': task.body}

    def _finish_approve(self, request, task_id=None, body=None,
                        approved=None, new_version=None):
        """
        If the task performer has edited this version, then we need to
        set the task's version to the new one that he has edited.
        """
        data = {'task': task_id, 'body': body, 'approved': approved}

        form = FinishApproveForm(request, data)

        if form.is_valid():
            task = form.cleaned_data['task']
            task.body = form.cleaned_data['body']
            task.approved = form.cleaned_data['approved']
            # if there is a new version, set that as the tasks's one
            if new_version:
                task.subtitle_version = new_version
            task.save()

            if task.approved in Task.APPROVED_FINISHED_IDS:
                task.complete()

            task.subtitle_version.language.release_writelock()

            if form.cleaned_data['approved'] == Task.APPROVED_IDS['Approved']:
                user_message =  'These subtitles have been approved and your notes have been sent to the author.'
                api_subtitles_approved.send(task.subtitle_version)
            elif form.cleaned_data['approved'] == Task.APPROVED_IDS['Rejected']:
                user_message =  'These subtitles have been rejected and your notes have been sent to the author.'
                api_subtitles_rejected.send(task.subtitle_version)
            else:
                user_message =  'Your notes have been saved.'

            video_changed_tasks.delay(task.team_video.video_id)
            return {'response': 'ok', 'user_message': user_message}
        else:
            return {'error_msg': _(u'\n'.join(flatten_errorlists(form.errors)))}


    def _find_base_language(self, base_language):
        if base_language:
            video = base_language.video
            if base_language.is_original or base_language.is_forked:
                return base_language
            else:
                if base_language.standard_language:
                    return base_language.standard_language
                else:
                    return video.subtitle_language()
        else:
            return None

    def _needs_new_sub_language(self, language, base_language):
        if language.standard_language and not base_language:
            # forking existing
            return False
        elif language.is_forked and base_language:
            return True
        else:
            return language.standard_language != base_language

    def _get_language_for_editing(
        self, request, video_id, language_code,
        subtitle_language_pk=None, base_language=None):

        video = models.Video.objects.get(video_id=video_id)

        editable = False
        create_new = False

        if subtitle_language_pk is not None:
            language = models.SubtitleLanguage.objects.get(pk=subtitle_language_pk)
            if self._needs_new_sub_language(language, base_language):
                create_new = True
            else:
                editable = language.can_writelock(request)
        else:
            create_new = True
        if create_new:
            standard_language = self._find_base_language(base_language)
            forked = standard_language is None
            language, created = models.SubtitleLanguage.objects.get_or_create(
                video=video,
                language=language_code,
                standard_language=standard_language,
                defaults={
                    'created': datetime.now(),
                    'is_forked': forked,
                    'writelock_session_key': '' })
            editable = created or language.can_writelock(request)
        if editable:
            language.writelock(request)
            language.save()
            if create_new:
                api_language_new.send(language)
        return language, editable

    def _fix_blank_original(self, video_id):
        # TODO: remove this method as soon as blank SubtitleLanguages
        # become illegal
        video = models.Video.objects.get(video_id=video_id)
        originals = video.subtitlelanguage_set.filter(is_original=True, language='')
        to_delete = []
        if len(originals) > 0:
            for original in originals:
                if not original.latest_version():
                    # result of weird practice of saving SL with is_original=True
                    # and blank language code on Video creation.
                    to_delete.append(original)
                else:
                    # decided to mark authentic blank originals as English.
                    original.language = 'en'
                    original.save()
        for sl in to_delete:
            sl.delete()

    def _save_original_language(self, video_id, language_code):
        video = models.Video.objects.get(video_id=video_id)
        has_original = False
        for sl in video.subtitlelanguage_set.all():
            if sl.is_original and sl.language != language_code:
                sl.is_original = False
                sl.save()
            elif not sl.is_original and sl.language == language_code:
                sl.is_original = True
                sl.save()
            if sl.is_original:
                has_original = True
        if not has_original:
            sl = models.SubtitleLanguage(
                video=video,
                language=language_code,
                is_forked=True,
                is_original=True,
                writelock_session_key='')
            sl.save()

    def _autoplay_subtitles(self, user, video_id, language_pk, version_no):
        cache =  video_cache.get_subtitles_dict(
            video_id, language_pk, version_no,
            lambda version: self._subtitles_dict(version))
        if cache and cache.get("language", None) is not None:
            cache['language_code'] = cache['language'].language
            cache['language_pk'] = cache['language'].pk
        return cache

    def _subtitles_dict(self, version, forced_version_no=None, force_forked=False):
        language = version.language
        base_language = None
        if language.is_dependent() and not version.is_forked and not force_forked:
            base_language = language.standard_language
        version_no = version.version_no if forced_version_no is None else forced_version_no
        is_latest = False
        latest_version = language.latest_version()
        if latest_version is None or version_no >= latest_version.version_no:
            is_latest = True
        return self._make_subtitles_dict(
            [s.__dict__ for s in version.subtitles()],
            language.language,
            language.pk,
            language.is_original,
            None if base_language is not None else language.is_complete,
            version_no,
            is_latest,
            version.is_forked or force_forked,
            base_language,
            language.get_title(),
            language.get_description()
        )


def language_summary(language, team_video=-1, user=None):
    """Return a dictionary of info about the given SubtitleLanguage.

    The team video can be given to avoid an extra database lookup.

    """
    if team_video == -1:
        team_video = language.video.get_team_video()

    summary = {
        'pk': language.pk,
        'language': language.language,
        'dependent': language.is_dependent(),
        'subtitle_count': language.subtitle_count,
        'in_progress': language.is_writelocked,
        'disabled_from': False,
        'disabled_to': False }

    if team_video:
        tasks = team_video.task_set.incomplete().filter(language=language.language)
        if tasks:
            task = tasks[0]
            if user and user != task.assignee:
                summary['disabled_to'] = True

    if not language.latest_version():
        summary['disabled_from'] = True

    if language.is_dependent():
        summary['percent_done'] = language.percent_done
        if language.standard_language:
            summary['standard_pk'] = language.standard_language.pk
    else:
        summary['is_complete'] = language.is_complete

    return summary
