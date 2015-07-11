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

from social_auth.backends.pipeline.social import social_auth_user
from social_auth.backends.google import GoogleBackend

def migrate_from_openid(backend, **kwargs):
    """Attempt to attach google openid clients to google-oauth2 clients"""
    if backend.name != 'google-oauth2':
        return None
    ret = social_auth_user(backend=GoogleBackend(), **kwargs)
    if ret.get('social_user', None):
        ret['social_user'].provider = 'google-oauth2'
    return ret

