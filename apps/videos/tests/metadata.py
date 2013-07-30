from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.utils import translation
from django.test import TestCase
import mock

from utils import test_factories, test_utils
from utils.celery_search_index import update_search_index
from videos.models import Video
from videos.search_indexes import VideoIndex
from subtitles import pipeline

class MetadataFieldsTest(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.video = test_factories.create_video()

    def test_metadata_starts_blank(self):
        version = pipeline.add_subtitles(self.video, 'en', None)
        self.assertEquals(self.video.get_metadata(), {})
        self.assertEquals(version.get_metadata(), {})

    def test_add_metadata_through_version(self):
        metadata = {
            'speaker-name': 'Santa',
            'location': 'North Pole',
        }
        version = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata=metadata)
        self.assertEquals(version.get_metadata(),  metadata)
        # the video should still have no metadata set
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertEquals(self.video.get_metadata(), {
            'speaker-name': '',
            'location': '',
        })

    def test_update_video(self):
        # test that when we set metadata for the primary language, it updates
        # the video's metadata
        self.video.update_metadata({'speaker-name': 'Speaker1'})
        self.assertEquals(self.video.get_metadata(),
                          {'speaker-name': 'Speaker1'})
        self.video.update_metadata({'speaker-name': 'Speaker2'})
        self.assertEquals(self.video.get_metadata(),
                          {'speaker-name': 'Speaker2'})

    def test_add_metadata_doesnt_change_video(self):
        # When we set metadata for a a language, it shouldn't update the video
        self.video.update_metadata({'speaker-name': 'Speaker1'})
        self.video.primary_audio_language_code = 'en'
        self.video.save()
        version = pipeline.add_subtitles(
            self.video, 'en', None,
            metadata={'speaker-name': 'Speaker2'})
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertEquals(self.video.get_metadata(),
                          {'speaker-name': 'Speaker1'})

    def test_add_metadata_twice(self):
        metadata_1 = {
            'speaker-name': 'Santa',
            'location': 'North Pole',
        }
        metadata_2 = {
            'speaker-name': 'Santa2',
            'location': 'North Pole2',
        }
        version = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata=metadata_1)
        version2 = pipeline.add_subtitles(self.video, 'en', None,
                                          metadata=metadata_2)
        self.assertEquals(version2.get_metadata(),  metadata_2)
        self.assertEquals(version.get_metadata(),  metadata_1)

    def test_languages_without_metadata(self):
        # languages without metadata set shouldn't get the metadata from other
        # languages
        metadata = {
            'speaker-name': 'Santa',
            'location': 'North Pole',
        }
        version = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata=metadata)
        version2 = pipeline.add_subtitles(self.video, 'fr', None,
                                          metadata=None)
        self.assertEquals(version2.get_metadata(),  {
            'speaker-name': '',
            'location': '',
        })

    def test_additional_field_in_update(self):
        metadata_1 = { 'speaker-name': 'Santa', }
        metadata_2 = {
            'speaker-name': 'Santa',
            'location': 'North Pole',
        }
        # version 1 only has 1 field
        version = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata=metadata_1)
        # version 2 only has 2 fields
        version2 = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata=metadata_2)
        # we should add the additional field in the version
        self.assertEquals(version2.get_metadata(),  metadata_2)

    def test_field_missing_in_update(self):
        metadata_1 = {
            'speaker-name': 'Santa',
            'location': 'North Pole',
        }
        metadata_2 = { 'speaker-name': 'Santa', }
        # version 1 only has 2 fields
        version = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata=metadata_1)
        # version 2 only has 1 field
        version2 = pipeline.add_subtitles(self.video, 'en', None,
                                          metadata=metadata_2)
        # version2 should not have data for location
        self.assertEquals(version2.get_metadata(), {
            'speaker-name': 'Santa',
            'location': '',
        })

    def test_metadata_display(self):
        version = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata={
                                             'speaker-name': 'Santa',
                                             'location': 'North Pole',
                                         })
        self.assertEquals(version.get_metadata().convert_for_display(), [
            { 'label': 'Speaker Name', 'content': 'Santa'},
            { 'label': 'Location', 'content': 'North Pole'},
        ])

    def test_metadata_display_is_translated(self):
        version = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata={
                                             'speaker-name': 'Santa',
                                             'location': 'North Pole',
                                         })
        with mock.patch('apps.videos.metadata._') as mock_gettext:
            mock_gettext.return_value = 'Mock Translation'
            metadata = version.get_metadata()
            self.assertEquals(metadata.convert_for_display(), [
                { 'label': 'Mock Translation', 'content': 'Santa'},
                { 'label': 'Mock Translation', 'content': 'North Pole'},
            ])

    def test_metadata_searchable(self):
        version = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata={
                                             'speaker-name': 'Santa',
                                             'location': 'North Pole',
                                         })
        update_search_index.apply(args=(Video, self.video.pk))
        qs = VideoIndex.public().filter(text='santa')
        self.assertEquals([v.video_id for v in qs], [self.video.video_id])

    def test_metadata_content_empty(self):
        self.video.update_metadata({'speaker-name': ''})
        # get_metadata() should return metadata with the key
        self.assertEquals(self.video.get_metadata(), {'speaker-name': ''})
        # but convert_for_display() should eliminate the value
        self.assertEquals(self.video.get_metadata().convert_for_display(), [])

class MetadataViewsTest(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.video = test_factories.create_video()
        self.video.update_metadata({
            'location': 'Place',
        })
        pipeline.add_subtitles(self.video, 'fr', None, metadata={
            'location': 'Place-fr',
        })

    def check_response_location(self, correct_location):
        url = reverse('videos:video_with_title', kwargs={
            'video_id': self.video.video_id,
            'title': self.video.title_for_url(),
        })
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['metadata'][0]['content'],
                          correct_location)

    def test_locale_with_metadata(self):
        translation.activate('fr')
        self.check_response_location('Place-fr')

    def test_locale_without_metadata(self):
        translation.activate('de')
        self.check_response_location('Place')
