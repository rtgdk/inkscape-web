#
# Copyright 2016, Martin Owens <doctormo@gmail.com>
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
"""
Useful and generic tools for the base class or other plugins.
"""

# A dictionary of names -> email addresses
EMAIL_ADDRESSES = defaultdict(set)

def parse_email(email):
    name = ''
    for (start, end) in (('<','>'), ('[mailto:', ']')):
        if email and start in email:
            (name, email) = email.split(start, 1)
            email = email.split(end, 1)[0]
    if email and '@' not in email:
        return (email, None)
    return (name.strip(), email.strip())


