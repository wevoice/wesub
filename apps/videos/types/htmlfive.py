# Amara, universalsubtitles.org
# 
# Copyright (C) 2013-2015 Participatory Culture Foundation
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

import subprocess, sys, re
from videos.types.base import VideoType

import logging
logger= logging.getLogger(__name__)

def getDurationFromStreams(streams):
    # this tries to get around most known cases
    # of duration set with issues in headers
    data = {}
    durations = set()
    index = None
    for line in streams.splitlines():
        index_m = re.match(r"index=(\w+)", line)
        if index_m:
            index = index_m.group(1)
            data[index] = {}
        duration_m = re.match(r"duration=(\w+)", line)
        if duration_m and index:
            duration = duration_m.group(1)
            data[index]["duration"]=int(float(duration))
        codec_m = re.match(r"codec_name=(\w+)", line)
        if codec_m and index:
            codec = codec_m.group(1)
            data[index]["codec"]=codec
        codec_type_m = re.match(r"codec_type=(\w+)", line)
        if codec_type_m and index:
            codec_type = codec_type_m.group(1)
            data[index]["codec_type"]=codec_type
        frames_m = re.match(r"nb_frames=(\w+)", line)
        if frames_m and index:
            frames = frames_m.group(1)
            try:
                data[index]["frames"]=int(frames)
            except:
                pass
    for key, val in data.items():
        if "duration" in val and val["duration"] > 0 and "codec" in val and val["codec"] != "unknown":
            if not ("frames" in val and
                    "codec_type" in val and
                    (val["codec_type"] == "video") and
                    ((val["frames"] / 25 / val["duration"] > 1.1) or (val["frames"] / 25 / val["duration"] < 0.9))):
                durations.add(val["duration"])
    if len(durations) == 1:
        return durations.pop()
    return None

class HtmlFiveVideoType(VideoType):
    abbreviation = 'H'
    name = 'HTML5'

    valid_extensions = set(['ogv', 'ogg', 'mp4', 'm4v', 'webm'])

    def __init__(self, url):
        self.url = url

    @classmethod
    def matches_video_url(cls, url):
        return cls.url_extension(url) in cls.valid_extensions

    def get_direct_url(self, prefer_audio=False):
        return self.url

    def set_values(self, video):
        cmd = """avprobe -v error -show_format -show_streams "{}" 2>&1 """.format(self.url)
        try:
            streams = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            duration = getDurationFromStreams(streams)
            video.duration = duration
        except subprocess.CalledProcessError as e:
            logger.error("CalledProcessError error({}) when running command {}".format(e.returncode, cmd))
        except:
            logger.error("Unexpected error({}) when running command {}".format(sys.exc_info()[0], cmd))
