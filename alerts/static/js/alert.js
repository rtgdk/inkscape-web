//
// Copyright 2015, Martin Owens <doctormo@gmail.com>
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

function update_screen() {
  if($('#items').children().length == 0) {
    $('#empty').show();
    $('.runner').remove();
    $('.pagination').remove();
  }
}

$(document).ready(function() {
  update_screen();
  $('.runner').submit(function() {
    $.getJSON($(this).attr("action"), function(data) {
      if(data['view'] != undefined) {
        $.each(data['view'], function (key, item) {
          $('#alert_'+item+" form.read").remove();
        });
      }
      if(data['delete'] != undefined) {
        $.each(data['delete'], function (key, item) {
          $('#alert_'+item).remove();
        });
      }
      update_screen();
    });
    $(this).remove();
    return false;
  });
});
