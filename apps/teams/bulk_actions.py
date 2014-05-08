from django.contrib.contenttypes.models import ContentType
from subtitles.models import SubtitleLanguage

def complete_approve_tasks(tasks):
    lang_ct = ContentType.objects.get_for_model(SubtitleLanguage)
    for task in tasks:
        task.do_complete_approve(lang_ct=lang_ct)
