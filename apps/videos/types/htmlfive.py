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

from videos.types.base import VideoType
import subprocess, sys, uuid
import logging
logger = logging.getLogger("HTML5 type")

class HtmlFiveVideoType(VideoType):
    abbreviation = 'H'
    name = 'HTML5'

    valid_extensions = set(['ogv', 'ogg', 'mp4', 'm4v', 'webm'])

    def __init__(self, url):
        self.url = url

    @classmethod
    def matches_video_url(cls, url):
        return cls.url_extension(url) in cls.valid_extensions

    def get_audio_file(self):
        # File is read from its URL, then converted to mono, in was
        # so that we do not lose quality with another encoding
        # TODO: find some way to protect ourselves from huge files
        output = "/tmp/" + str(uuid.uuid4()) + ".wav"
        cmd = """avconv -i "{}" -ar 16000 -ac 1 {}""".format(self.url, output)
        try:
            subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            logger.error("CalledProcessError error({}) when running command {}".format(e.returncode, cmd))
            return None
        except:
            logger.error("Unexpected error({}) when running command {}".format(sys.exc_info()[0], cmd))
            return None
        return output
