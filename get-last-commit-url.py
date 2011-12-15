#!/usr/bin/env python

# Requirements
# pip install pyquery requests
# PyQuery: http://pypi.python.org/pypi/pyquery
# Requests: http://docs.python-requests.org/en/latest/index.html

import re, requests, sys
from pyquery import PyQuery as pq


def main():
    r = requests.get('https://github.com/pculture/unisubs/commits/ongoing')
    J = pq(r.content)

    commits = J('p.commit-title')
    coms = []

    for commit in commits:
        if not re.match('.*merge.*', J(commit).text(), flags=re.IGNORECASE):
            coms.append(commit)

    title = '%s\n\n' % J('a', coms[0]).eq(0).text()
    sys.stderr.write(title)

    sys.stdout.write('https://github.com%s'.rstrip() % J('a', coms[0]).attr('href'))

if __name__ == '__main__':
    main()
