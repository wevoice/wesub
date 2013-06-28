# Amara, universalsubtitles.org
#
# Copyright (C) 2013 Participatory Culture Foundation
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

"""videos.metadata - Handle metadata fields stored for videos and versions

Videos store metadata fields using the meta_N_type and meta_N_content columns.

Types for metadata fields have several different representations:
    - They are stored in the database as integers.
    - The getter/setter methods use a string machine name (these are nicer for
      using in JSON dicts and the like).
    - When displaying them, we use a human-friendly, translated, labels.

There is also support for an having other models use the fields from video and
optionally override them.  To implement that, you need to add the
meta_N_content columns to your model, and use update_child_and_video()
and get_metadata_for_child() functions to get/set the metadata data.
This is currently used by SubtitleVersion
"""

from django.db import models
from django.template.defaultfilters import slugify
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_noop

try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([], [
        "^videos\.metadata\.Metadata.*Field",
        "^apps\.videos\.metadata\.Metadata.*Field",
    ])

METADATA_FIELD_COUNT = 3

# Define possible values for the metadata type fields.  List of
# (db_value, label) tuples.  The name will be computed by slugifying the label
metadata_type_choices = [
    (0, ugettext_noop('Speaker Name')),
    (1, ugettext_noop('Location')),
]

type_value_to_name = dict((val, slugify(label))
                         for val, label in metadata_type_choices)
name_to_type_value = dict((slugify(label), val)
                         for val, label in metadata_type_choices)
name_to_label = dict((slugify(label), label)
                     for val, label in metadata_type_choices)

def type_name_is_valid(name):
    return name in name_to_type_value

def type_field(index):
    return 'meta_%s_type' % (index+1)

def content_field(index):
    return 'meta_%s_content' % (index+1)

class MetadataTypeField(models.PositiveIntegerField):
    def __init__(self, **kwargs):
        kwargs.update({
            'null': True,
            'blank': True,
            'choices': metadata_type_choices,
        })
        models.PositiveIntegerField.__init__(self, **kwargs)

class MetadataContentField(models.CharField):
    def __init__(self, **kwargs):
        kwargs.update({
            'blank': True,
            'max_length': 255,
            'default': '',
        })
        models.CharField.__init__(self, **kwargs)

class MetadataFieldList(list):
    def convert_for_display(self):
        """Convert the types in this list to human-friendly labels.

        Also converts the tuples to a dict for easy use in the template system
        """

        return [{
            'label': _(name_to_label[name]),
            'content': content,
        } for name, content in self]

def get_fields_for_video(video):
    """Get a list of metadata for a video

    :returns: list of (name, content) tuples
    """
    rv = MetadataFieldList()
    for i in xrange(METADATA_FIELD_COUNT):
        type_val = getattr(video, type_field(i))
        if type_val is None:
            break
        else:
            rv.append((type_value_to_name[type_val],
                       getattr(video, content_field(i))))
    return rv

def update_video(video, field_data, commit=True):
    """Update a video object bassed on a list of field data

    This method sets the type/content fields on video if needed, then returns
    the content so that it can be set for on the fields of SubtitleVersion.

    :param video: Video object to update
    :param field_data: data for the fields as a list of (name, content) tuples
    :returns: a list of content values, in the same order as the fields are
    ordered (rv[N] corrsponds for the meta_N_type on video).
    """
    rv = []
    field_data_map = SortedDict(field_data)
    # go through metadata already stored in the video
    for field_index in xrange(METADATA_FIELD_COUNT):
        type_value = getattr(video, type_field(field_index))
        if type_value is None:
            break
        type_name = type_value_to_name[type_value]
        if type_name in field_data_map:
            rv.append(field_data_map.pop(type_name))
        else:
            rv.append('')
    # go through metadata not yet stored in the video
    # NOTE: after the loop, field_index points to the first metadata that's
    # unused
    changed_video = False
    for name, content in field_data_map.items():
        type_value = name_to_type_value[name]
        if field_index >= METADATA_FIELD_COUNT:
            raise ValueError("Can only store %s metadata" %
                             METADATA_FIELD_COUNT)
        setattr(video, type_field(field_index), type_value)
        setattr(video, content_field(field_index), content)
        rv.append(content)
        field_index += 1
        changed_video = True
    if changed_video and commit:
        video.save()
    return rv

def update_child_and_video(child, video, field_data, commit=True):
    """Update metadata for both a video and a child object """
    content_data = update_video(video, field_data, commit)
    for i, content in enumerate(content_data):
        setattr(child, content_field(i), content)
    if commit:
        child.save()

def get_child_metadata(child, video):
    """Get the metadata data for a child."""
    rv = MetadataFieldList()
    video_metadata = video.get_metadata()
    for i, (name, video_content) in enumerate(video_metadata):
        child_content = getattr(child, content_field(i))
        if child_content:
            rv.append((name, child_content))
        else:
            rv.append((name, video_content))
    return rv
