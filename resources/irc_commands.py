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
IRC Commands related to resources and artwork.
"""

from inkscape.management.commands.ircbot import BotCommand

from .models import Category

class LatestArtCommand(BotCommand):
    regex = "Get Latest Art"

    def run_command(self):
        try:
            artworks = Category.objects.get(name='Artwork')
        except Category.DoesNotExist:
            return "No Artworks Category on website"

        try:
            art = artworks.items.filter(published=True).latest('created')
        except Resource.DoesNotExist:
            return "No Artworks uploaded yet"

        return u"%s by %s: %s" % (unicode(art), unicode(art.user), url(art))

