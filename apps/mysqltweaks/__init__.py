# Amara, universalsubtitles.org
#
# Copyright (C) 2016 Participatory Culture Foundation
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
"""
This app monkeypatches django to support adding FORCE INDEX to the FROM
clause for MySQL.
"""

from django.db.backends.mysql import compiler

class PatchedSQLCompiler(compiler.SQLCompiler):
    def get_from_clause(self):
        result, params = super(PatchedSQLCompiler, self).get_from_clause()
        if getattr(self.query, 'force_index', False):
            result[0] += ' FORCE INDEX({})'.format(
                self.connection.ops.quote_name(self.query.force_index))
        return result, params

def monkeypatch():
    compiler.SQLCompiler = PatchedSQLCompiler
