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

# override the default loader
from django.db import connection
from djcelery.loaders import DjangoLoader

class AmaraCeleryLoader(DjangoLoader):
    def close_database(self, **kwargs):
        # DjangoLoader sometimes reuses connections.  Make sure our current
        # transaction is commited in that case.
        connection.cursor().execute("COMMIT")
        DjangoLoader.close_database(self, **kwargs)
