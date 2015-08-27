#
# Copyright 2015, Martin Owens <doctormo@gmail.com>
#
# This file is part of the software inkscape-web, consisting of custom 
# code for the Inkscape project's django-based website.
#
# inkscape-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# inkscape-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with inkscape-web.  If not, see <http://www.gnu.org/licenses/>.
#

from django.db.models import *

from django.utils.translation import ugettext_lazy as _

class ErrorLog(Model):
    uri    = CharField(max_length=255, db_index=True)
    status = IntegerField(db_index=True)
    count  = IntegerField(default=0)
    added  = DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return "%s (%d)" % (self.uri, self.status)

    def add(self):
        self.count += 1
        self.save()

