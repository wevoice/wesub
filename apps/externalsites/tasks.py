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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.


from celery.task import task

@task
def update_subtitles(account_type, account_id, lang_id, version_id):
    """Update a subtitles for a language"""
    print 'update_subtitles: (%s, %s, %s)' % (account_type, account_id,
                                              lang_id, version_id)

@task
def delete_subtitles(account_type, account_id, lang_id):
    """Delete a subtitles for a language"""
    print 'delete_subtitles: (%s, %s)' % (account_type, account_id, lang_id)

@task
def update_all_subtitles(account_type, account_id):
    """Update all subtitles for a given account."""
    print 'update_all_subtitles: %s' % (account_type, account_id)
