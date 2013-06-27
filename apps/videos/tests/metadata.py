from __future__ import absolute_import

from django.test import TestCase
import mock

from utils import test_factories, test_utils
from videos.models import Video
from videos.search_indexes import VideoIndex
from subtitles import pipeline

class MetadataFieldsTest(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.video = test_factories.create_video()
    
    def test_metadata_starts_blank(self):
        version = pipeline.add_subtitles(self.video, 'en', None)
        self.assertEquals(self.video.get_metadata(), [])
        self.assertEquals(version.get_metadata(), [])

    def test_add_metadata(self):
        metadata=[
                ('speaker-name', 'Santa'),
                ('location', 'North Pole'),
        ]
        version = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata=metadata)
        self.assertEquals(version.get_metadata(),  metadata)
        # should also add the fields to the video
        self.assertEquals(self.video.get_metadata(),  metadata)

    def test_add_metadata_twice(self):
        metadata_1 = [
                ('speaker-name', 'Santa'),
                ('location', 'North Pole'),
        ]
        metadata_2 = [
                ('speaker-name', 'Santa2'),
                ('location', 'North Pole2'),
        ]
        version = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata=metadata_1)
        version2 = pipeline.add_subtitles(self.video, 'en', None,
                                          metadata=metadata_2)
        self.assertEquals(version2.get_metadata(),  metadata_2)
        self.assertEquals(version.get_metadata(),  metadata_1)
        # video should have the values given the first time
        self.assertEquals(self.video.get_metadata(),  metadata_1)

    def test_new_languages_get_metadata(self):
        metadata = [
                ('speaker-name', 'Santa'),
                ('location', 'North Pole'),
        ]
        version = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata=metadata)
        version2 = pipeline.add_subtitles(self.video, 'fr', None,
                                          metadata=None)
        self.assertEquals(version2.get_metadata(),  metadata)

    def test_additional_field_in_update(self):
        metadata_1 = [
                ('speaker-name', 'Santa'),
        ]
        metadata_2 = [
                ('speaker-name', 'Santa'),
                ('location', 'North Pole'),
        ]
        # version 1 only has 1 field
        version = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata=metadata_1)
        # version 2 only has 2 fields
        version2 = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata=metadata_2)
        # we should add the additional field to both the version and the video
        updated_video = Video.objects.get(pk=self.video.pk)
        self.assertEquals(version2.get_metadata(),  metadata_2)
        self.assertEquals(updated_video.get_metadata(),  metadata_2)

    def test_field_missing_in_update(self):
        metadata_1 = [
                ('speaker-name', 'Santa'),
                ('location', 'North Pole'),
        ]
        metadata_2 = [
                ('location', 'Workshop'),
        ]
        # version 1 only has 2 fields
        version = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata=metadata_1)
        # version 2 only has 1 field
        version2 = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata=metadata_2)
        # version2 should inherit the value for speaker name from the
        # video/version 1 and override the value for location
        self.assertEquals(version2.get_metadata(), [
            ('speaker-name', 'Santa'),
            ('location', 'Workshop'),
        ])

    def test_order_different_in_update(self):
        metadata_1 = [
                ('speaker-name', 'Santa'),
                ('location', 'North Pole'),
        ]
        metadata_2 = [
                ('location', 'North Pole'),
                ('speaker-name', 'Santa'),
        ]
        version = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata=metadata_1)
        version2 = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata=metadata_2)
        # We should order fields in the order the were first added in
        self.assertEquals(version2.get_metadata(),  metadata_1)

    def test_metadata_labels(self):
        version = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata=[
                                             ('speaker-name', 'Santa'),
                                             ('location', 'North Pole'),
                                         ])
        self.assertEquals(version.get_metadata().convert_for_display(), [
            ('Speaker Name', 'Santa'),
            ('Location', 'North Pole'),
        ])

    def test_metadata_labels_are_translated(self):
        version = pipeline.add_subtitles(self.video, 'en', None,
                                         metadata=[
                                             ('speaker-name', 'Santa'),
                                             ('location', 'North Pole'),
                                         ])
        with mock.patch('apps.videos.metadata._') as mock_gettext:
            mock_gettext.return_value = 'Mock Translation'
            metadata = version.get_metadata()
            self.assertEquals(metadata.convert_for_display(), [
                ('Mock Translation', 'Santa'),
                ('Mock Translation', 'North Pole'),
            ])
