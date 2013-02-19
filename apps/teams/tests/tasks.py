import datetime
import simplejson as json

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
import mock

from auth.models import CustomUser as User
from apps.teams.forms import TaskCreateForm, TaskAssignForm
from apps.teams.models import Task, Team, TeamVideo, TeamMember
from apps.videos.models import Video
from utils.tests import TestEditor
from utils import test_factories

# review setting constants
DONT_REQUIRE_REVIEW = 0
PEER_MUST_REVIEW = 10
MANAGER_MUST_REVIEW = 20
ADMIN_MUST_REVIEW = 30
# approval setting contants
DONT_REQUIRE_APPROVAL = 0
MANAGER_MUST_APPROVE = 10
ADMIN_MUST_APPROVE = 20
# task type constants
TYPE_SUBTITLE = 10
TYPE_TRANSLATE = 20
TYPE_REVIEW = 30
TYPE_APPROVE = 40

class AutoCreateTest(TestCase):

    def setUp(self):
        self.team = test_factories.create_team(workflow_enabled=True)
        w = test_factories.create_workflow(self.team,
                                           autocreate_subtitle=True,
                                           autocreate_translate=True)
        self.admin = test_factories.create_team_member(
            self.team, role=TeamMember.ROLE_ADMIN)

    def test_no_audio_language(self):
        video = test_factories.create_video(primary_audio_language_code='')
        tv = test_factories.create_team_video(self.team, self.admin.user,
                                              video)
        tasks = tv.task_set.all()
        self.assertEqual(tasks.count() , 1)
        transcribe_task = tasks.filter(type=10, language='')
        self.assertEqual(transcribe_task.count(), 1)

    def test_audio_language(self):
        # create the original language for this video
        video = test_factories.create_video(primary_audio_language_code='en')
        tv = test_factories.create_team_video(self.team, self.admin.user,
                                              video)
        tasks = tv.task_set.all()
        self.assertEqual(tasks.count() , 1)
        transcribe_task = tasks.filter(type=10, language='en')
        self.assertEqual(transcribe_task.count(), 1)

class TranscriptionTaskTest(TestCase):
    """Tests for transcription tasks."""

    def setUp(self):
        self.team = test_factories.create_team(workflow_enabled=True)
        self.workflow = test_factories.create_workflow(
            self.team,
            review_allowed=DONT_REQUIRE_REVIEW,
            approve_allowed=DONT_REQUIRE_APPROVAL)
        self.admin = test_factories.create_team_member(
            self.team, role=TeamMember.ROLE_ADMIN)
        self.team_video = test_factories.create_team_video(self.team,
                                                           self.admin.user)
        self.client = Client()
        self.login(self.admin.user)

    def login(self, user):
        self.client.login(username=user.username, password="password")

    def get_subtitle_task(self):
        tasks = list(self.team_video.task_set.all_subtitle().all())
        self.assertEqual(len(tasks), 1)
        return tasks[0]

    def get_review_task(self):
        tasks = list(self.team_video.task_set.all_review().all())
        self.assertEqual(len(tasks), 1)
        return tasks[0]

    def get_approve_task(self):
        tasks = list(self.team_video.task_set.all_approve().all())
        self.assertEqual(len(tasks), 1)
        return tasks[0]

    def check_incomplete_counts(self, subtitle_count, review_count,
                                approve_count):
        self.assertEquals(
            self.team_video.task_set.incomplete_subtitle().count(),
            subtitle_count)
        self.assertEquals(
            self.team_video.task_set.incomplete_review().count(),
            review_count)
        self.assertEquals(
            self.team_video.task_set.incomplete_approve().count(),
            approve_count)

    def delete_tasks(self):
        self.team_video.task_set.all().delete()

    def submit_assign(self, member, task, ajax=False):
        if ajax:
            url_name = 'teams:assign_task_ajax'
        else:
            url_name = 'teams:assign_task'
        url = reverse(url_name, kwargs={'slug': self.team.slug})
        post_data = {'task': task.pk, 'assignee': member.user.pk}
        return self.client.post(url, post_data)

    def submit_create_task(self, type, assignee='', expecting_error=False):
        url = reverse('teams:create_task',
                             kwargs={'slug': self.team.slug,
                                     'team_video_pk': self.team_video.pk})
        post_data = {'type': type, 'language': '', 'assignee': assignee}
        response = self.client.post(url, post_data)
        # This isn't the best way to check, but if the form was had an error,
        # than the status code will be 200, since we don't redirect in that
        # case.
        form_had_error = (response.status_code == 200)
        if not expecting_error and form_had_error:
            form = response.context['form']
            raise AssertionError("submit to %s failed -- errors:\n%s" %
                                 (url, form.errors.as_text()))
        elif expecting_error and not form_had_error:
            raise AssertionError("submit to %s succeeded" % url)

    def perform_subtitle_task(self, task):
        editor = TestEditor(self.client, self.team_video.video)
        editor.run()

    def perform_review_task(self, task, notes=None):
        editor = TestEditor(self.client, self.team_video.video, mode="review")
        editor.set_task_data(task, Task.APPROVED_IDS['Approved'], notes)
        editor.run()

    def perform_approve_task(self, task, notes=None):
        editor = TestEditor(self.client, self.team_video.video,
                mode="approve")
        editor.set_task_data(task, Task.APPROVED_IDS['Approved'], notes)
        editor.run()

    def change_workflow_settings(self, review_allowed, approve_allowed):
        self.workflow.review_allowed = review_allowed
        self.workflow.approve_allowed = approve_allowed
        self.workflow.save()

    def create_member(self):
        return test_factories.create_team_member(
            self.team, role=TeamMember.ROLE_CONTRIBUTOR)

    def test_create(self):
        self.submit_create_task(TYPE_SUBTITLE)
        task = self.get_subtitle_task()
        self.assertEqual(task.type, TYPE_SUBTITLE)
        self.assertEqual(task.language, '')
        self.assertEqual(task.assignee, None)

    def test_assign_on_create_form(self):
        member = self.create_member()
        self.submit_create_task(TYPE_SUBTITLE, assignee=member.user.pk)
        task = self.get_subtitle_task()
        self.assertEqual(task.assignee, member.user)

    def test_assign_with_form(self):
        # submit the task
        self.submit_create_task(TYPE_SUBTITLE)
        task = self.get_subtitle_task()
        # create a member and assign the task to them
        member = self.create_member()
        response = self.submit_assign(member, task)
        if ('form' in response.context and
            not response.context['form'].is_valid()):
            raise AssertionError("submit failed -- errors:\n%s" %
                                 response.context['form'].errors.as_text)
        # check that it worked
        task = self.get_subtitle_task()
        self.assertEquals(task.assignee, member.user)

    def test_assign_with_ajax(self):
        # submit the task
        self.submit_create_task(TYPE_SUBTITLE)
        task = self.get_subtitle_task()
        # create a member and assign the task to them
        member = self.create_member()
        response = self.submit_assign(member, task, ajax=True)
        if ('form' in response.context and
            not response.context['form'].is_valid()):
            raise AssertionError("submit failed -- errors:\n%s" %
                                 response.context['form'].errors.as_text)
        # check that it worked
        response_data = json.loads(response.content)
        self.assertEquals(response_data.get('success'), True)
        task = self.get_subtitle_task()
        self.assertEquals(task.assignee, member.user)

    def test_perform(self):
        member = self.create_member()
        self.submit_create_task(TYPE_SUBTITLE, member.user.pk)
        task = self.get_subtitle_task()
        self.login(member.user)
        self.perform_subtitle_task(task)
        task = Task.objects.get(pk=task.pk)
        self.assertNotEquals(task.completed, None)
        self.assertEquals(task.approved, None)
        self.check_incomplete_counts(0, 0, 0)

    def test_review(self):
        self.change_workflow_settings(ADMIN_MUST_REVIEW,
                                      DONT_REQUIRE_APPROVAL)
        member = self.create_member()
        self.submit_create_task(TYPE_SUBTITLE, member.user.pk)
        task = self.get_subtitle_task()
        self.login(member.user)
        self.perform_subtitle_task(task)
        # test test that the review is ready to go
        self.check_incomplete_counts(0, 1, 0)
        subtitle_language = self.team_video.video.subtitle_language()
        self.assertEquals(subtitle_language.get_tip().is_public(), False)
        # perform the review
        review_task = self.get_review_task()
        self.login(self.admin.user)
        self.submit_assign(self.admin, review_task)
        self.perform_review_task(review_task, "Test Note")
        # The review is now complete, check aftermath
        self.assertEquals(self.get_review_task().body, "Test Note")
        self.check_incomplete_counts(0, 0, 0)
        self.assertEquals(subtitle_language.get_tip().is_public(), True)

    def test_approve(self):
        self.change_workflow_settings(DONT_REQUIRE_REVIEW,
                                      ADMIN_MUST_APPROVE)
        self.workflow.save()
        member = self.create_member()
        self.submit_create_task(TYPE_SUBTITLE, member.user.pk)
        task = self.get_subtitle_task()
        self.login(member.user)
        self.perform_subtitle_task(task)
        # test test that the approval task is ready to go
        self.check_incomplete_counts(0, 0, 1)
        subtitle_language = self.team_video.video.subtitle_language()
        self.assertEquals(subtitle_language.get_tip().is_public(), False)
        # perform the approval
        approve_task = self.get_approve_task()
        self.login(self.admin.user)
        self.submit_assign(self.admin, approve_task)
        self.perform_approve_task(approve_task, "Test Note")
        # The approve is now complete, check aftermath
        self.assertEquals(self.get_approve_task().body, "Test Note")
        self.check_incomplete_counts(0, 0, 0)
        self.assertEquals(subtitle_language.get_tip().is_public(), True)

    def test_review_and_approve(self):
        self.change_workflow_settings(ADMIN_MUST_REVIEW,
                                      ADMIN_MUST_APPROVE)
        self.workflow.save()
        member = self.create_member()
        self.submit_create_task(TYPE_SUBTITLE, member.user.pk)
        task = self.get_subtitle_task()
        self.login(member.user)
        self.perform_subtitle_task(task)
        # test test that the review task is next
        self.check_incomplete_counts(0, 1, 0)
        subtitle_language = self.team_video.video.subtitle_language()
        self.assertEquals(subtitle_language.get_tip().is_public(), False)
        # perform the review
        review_task = self.get_review_task()
        self.login(self.admin.user)
        self.submit_assign(self.admin, review_task)
        self.perform_review_task(review_task, "Test Review Note")
        # check that that worked
        self.check_incomplete_counts(0, 0, 1)
        self.assertEquals(subtitle_language.get_tip().is_public(), False)
        self.assertEquals(self.get_review_task().body, "Test Review Note")
        # perform the approval
        approve_task = self.get_approve_task()
        self.submit_assign(self.admin, approve_task)
        self.perform_approve_task(approve_task, "Test Note")
        # The approve is now complete, check aftermath
        self.assertEquals(self.get_approve_task().body, "Test Note")
        self.check_incomplete_counts(0, 0, 0)
        self.assertEquals(subtitle_language.get_tip().is_public(), True)

    def test_due_date(self):
        self.team.task_expiration = 2
        self.team.save()
        # submit the task.  It shouldn't have an expiration date before it
        # gets assigned
        self.submit_create_task(TYPE_SUBTITLE)
        task = self.get_subtitle_task()
        self.assertEquals(task.expiration_date, None)
        # create a member and assign the task to them.  After thi, the
        # expiration date should be set.
        member = self.create_member()
        self.submit_assign(member, task)
        approx_expiration = (datetime.datetime.now() +
                             datetime.timedelta(days=2))
        expiration_date = self.get_subtitle_task().expiration_date
        self.assert_(approx_expiration - datetime.timedelta(seconds=1) <
                     expiration_date)
        self.assert_(approx_expiration + datetime.timedelta(seconds=1) >
                     expiration_date)

class TranslationTaskTest(TestCase):
    """Tests for translation tasks."""

    def test_create(self):
        pass

    def test_assign(self):
        pass

    def test_review(self):
        pass

    def test_approve(self):
        pass

    def test_create_permissions(self):
        pass

    def test_review_permissions(self):
        pass

    def test_approve_permissions(self):
        pass

    def test_due_date(self):
        pass
