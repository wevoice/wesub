"""
Video crop
==========

Given a video, create 100 small 10 second videos from that video.

Usage: $ video_crop.py FILENAME

Depends on ffmpeg.  `brew install ffmpeg`
"""

import os
from fabric.api import local


def pad(n):
    if n < 10:
        return '0' + str(n)
    return str(n)


def crop(src_filename):
    if not os.path.exists(src_filename):
        print "File doesn't exist"
        return

    command = "ffmpeg -ss {0} -t 00:00:10 -i {1} -acodec mp3 -vcodec copy {2}"

    minute = 0
    second = 0

    for n in range(1, 101):
        dest = 'test-video-{0}.avi'.format(pad(n))

        if minute == 0 and second == 0:
            start = '00:00:00'
        else:
            if second == 60:
                minute += 1
                second = 0

            start = '00:{0}:{1}'.format(pad(minute), pad(second))

        second += 10

        cmd = command.format(start, src_filename, dest)
        local(cmd)


if __name__ == '__main__':
    import sys
    try:
        crop(sys.argv[1])
    except IndexError:
        print 'Missing argument'
        print 'Usage: video_crop.py FILENAME'
