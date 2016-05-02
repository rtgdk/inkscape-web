//
// Copyright 2016, Martin Owens <doctormo@gmail.com>
//
// This file is part of the software inkscape-web, consisting of custom 
// code for the Inkscape project's django-based website.
//
// inkscape-web is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// inkscape-web is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with inkscape-web.  If not, see <http://www.gnu.org/licenses/>.
//

$(document).ready(function() {
  $("#readmore").click(function(e) {
    e.preventDefault();
    url = $(this).attr('href');
    $.ajax({
      url: url,
      async: false,
     dataType: "text",
      success: function(data) {
	 var descContent = data;
	 // cut off first three lines of text file, insert paragraphs
	 descContent = "<p>" + descContent.split("\n").slice(2).join("</p> <p>") + "</p>";
	 $(".desc").html(descContent);
	 // TODO: urls could be turned into clickable links
       },
    });
  });
});
