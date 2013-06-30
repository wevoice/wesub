from babelsubs.storage import SubtitleSet
from babelsubs.storage import diff as diff_subs
from babelsubs.generators.html import HTMLGenerator
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django import forms

from teams.models import Team
from subtitles import tern
from subtitles.models import (SubtitleLanguage, SubtitleVersion,
                              ORIGIN_DMR_CLEANUP)
from videos.models import Video
from videos.models import SubtitleLanguage as OldSubtitleLanguage
from videos.models import SubtitleVersion as OldSubtitleVersion

class NewSubtitleVersionWrapper(object):
    """Wrap a new subtitle version for displaying in the view.

    This wraps the subtitles.models.SubtitleVersion into the interface of
    videos.models.SubtitleVersion, at least well enough to make our views
    work.
    """
    
    def __init__(self, prev_sv, sv):
        self.version_no = sv.version_number
        self.datetime_started = sv.created
        self.user = sv.author
        self.is_public = sv.is_public()
        self.title = sv.title
        self.description = sv.description
        if prev_sv is not None:
            self.prev_title = prev_sv.title
            self.prev_description = prev_sv.description
        else:
            self.prev_title = sv.video.title
            self.prev_description = sv.video.description
        self.sv = sv
        self.prev_sv = prev_sv

    def get_diff(self):
        if self.prev_sv is not None:
            prev_subtitles = self.prev_sv.get_subtitles()
        else:
            prev_subtitles = SubtitleSet.from_list(
                self.sv.language_code, [])
        return diff_subs(prev_subtitles, self.sv.get_subtitles(),
                            HTMLGenerator.MAPPINGS)

def calc_added_after_tern(language):
    sql = ("SELECT ssv.* "
           "FROM subtitles_subtitleversion ssv "
           "LEFT JOIN videos_subtitleversion vsv "
           "ON ssv.id = vsv.new_subtitle_version_id "
           "WHERE vsv.new_subtitle_version_id IS NULL AND "
           "      ssv.subtitle_language_id=%s" % (language.pk,))
    versions = list(SubtitleVersion.objects.raw(sql))
    rv = []
    rv.append(NewSubtitleVersionWrapper(None, versions[0]))
    for i in xrange(1, len(versions)):
        rv.append(NewSubtitleVersionWrapper(versions[i-1], versions[i]))
    return rv

@user_passes_test(lambda user: user.is_staff)
def language_list(request):
    if request.GET.get('team'):
        team = Team.objects.get(slug=request.GET['team'])
    else:
        team = None
    LIMIT = 10
    qs = OldSubtitleLanguage.objects
    if team is not None:
        qs = qs.filter(video__teamvideo__team=team)
    qs = qs.extra(where=['videos_subtitlelanguage.id IN ('
                  'SELECT language_id FROM videos_subtitleversion '
                  'WHERE new_subtitle_version_id IS NULL AND needs_sync)'])
    qs = qs.order_by('video')
    return render(request, "subtitles/dmr-cleanup-list.html", {
        'languages': qs[:LIMIT],
        'extra_count': max(0, qs.count() - LIMIT),
        'selected_team': team,
        'teams': Team.objects.all(),
    })

def make_language_fixup_form(old_sl, new_sl):
    class DMRLanguageFixupForm(forms.Form):
        if new_sl and new_sl.subtitles_complete != old_sl.is_complete:
            subtitles_complete = forms.ChoiceField(choices=[
                (True, 'Complete'),
                (False, 'Incomplete'),
            ], initial=True)

        if new_sl and new_sl.is_forked != old_sl.is_forked:
            is_forked = forms.ChoiceField(choices=[
                (True, 'Forked'),
                (False, 'Unforked'),
            ], initial=True)

        new_versions = forms.ChoiceField(choices=[
            ('add', 'Add Pre-DMR Versions'),
            ('drop', 'Drop Pre-DMR Versions'),
        ], initial='add', widget=forms.RadioSelect)

        def has_different_language_data(self):
            return ('subtitles_complete' in self.fields or
                    'is_forked' in self.fields or
                    'visibility' in self.fields)
    return DMRLanguageFixupForm

def append_old_version(sv):
    """Stack the given version onto the given new SL."""
    from apps.subtitles import pipeline

    if sv.is_public:
        visibility = 'public'
    else:
        visibility = 'private'

    subtitles = list(tern._get_subtitles(sv))
    language_code = sv.language.language
    video = sv.language.video

    # set subtitle set as the pipeline will pass escaping
    # otherwise and it will break
    sset = SubtitleSet.from_list(language_code, subtitles)
    nsv = pipeline.add_subtitles(video, language_code, sset,
        title=sv.title, description=sv.description, parents=[],
        visibility=visibility, author=sv.user,
        created=sv.datetime_started, origin=ORIGIN_DMR_CLEANUP)

    sv.new_subtitle_version = nsv
    sv.needs_sync = False
    sv.save()

def handle_form_language(form_data, old_sl, new_sl):
    if new_sl is None:
        new_sl = SubtitleLanguage(video=old_sl.video,
                                  language_code=old_sl.language,
                                  subtitles_complete=old_sl.is_complete,
                                  is_forked=old_sl.is_forked)
    if 'subtitles_complete' in form_data:
        new_sl.subtitles_complete = form_data['subtitles_complete']
    if 'is_forked' in form_data:
        new_sl.is_forked = form_data['is_forked']
    new_sl.save()

def handle_form(form, old_sl, new_sl, missed_by_tern):
    form_data = form.cleaned_data
    handle_form_language(form_data, old_sl, new_sl)

    if form_data['new_versions'] == 'drop':
        for v in missed_by_tern:
            v.needs_sync = False
            v.save()
    else:
        for v in missed_by_tern:
            append_old_version(v)

@user_passes_test(lambda user: user.is_staff)
def language_fixup(request, video_id, language_code):
    video = Video.objects.get(video_id=video_id)
    old_sl = OldSubtitleLanguage.objects.get(video=video,
                                             language=language_code)
    try:
        new_sl = SubtitleLanguage.objects.get(video=video,
                                              language_code=language_code)
        added_after_tern = calc_added_after_tern(new_sl)
    except SubtitleLanguage.DoesNotExist:
        new_sl = None
        added_after_tern = []
    missed_by_tern = list(old_sl.subtitleversion_set
                          .filter(needs_sync=True,
                                  new_subtitle_version_id__isnull=True)
                          .order_by('version_no'))

    DMRLanguageFixupForm = make_language_fixup_form(old_sl, new_sl)
    if request.method == 'POST':
        form = DMRLanguageFixupForm(request.POST)
        if form.is_valid():
            handle_form(form, old_sl, new_sl, missed_by_tern)
            url = '/en/videos/%s/%s/' % (old_sl.video.video_id,
                                         old_sl.language)
            msg = u'Fixed language: <a href="%s">%s - %s</a>' % (
                url, old_sl.video, old_sl.language)
            messages.info(request, message=msg)
            return redirect('/en/subtitles/dmr-cleanup/')
    else:
        form = DMRLanguageFixupForm()

    return render(request, "subtitles/dmr-cleanup-language.html", {
        'missed_by_tern': missed_by_tern,
        'added_after_tern': added_after_tern,
        'form': form,
        'old_sl': old_sl,
        'new_sl': new_sl,
    })
