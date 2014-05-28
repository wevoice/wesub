from django.contrib.contenttypes.models import ContentType
from subtitles.models import SubtitleLanguage
from teams.signals import api_subtitles_approved
from videos.tasks import video_changed_tasks

def complete_approve_tasks(tasks):
    lang_ct = ContentType.objects.get_for_model(SubtitleLanguage)
    video_ids = set()
    for task in tasks:
        task.do_complete_approve(lang_ct=lang_ct)
        api_subtitles_approved.send(task.get_subtitle_version())
        video_ids.add(task.team_video.video_id)
    for video_id in video_ids:
        video_changed_tasks.delay(video_id)

