//
// Copyright 2014, Martin Owens <doctormo@gmail.com>
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

/* Page loading processes */
$(document).ready(function() {
  if($('#toc').length == 1) {
    initialise_anchors();
  }
});

$.fn.slugify = function() {
    var text = $(this).text();
    return text.replace(/\s+/g,'-').replace(/[^a-zA-Z0-9\-]/g,'').toLowerCase();
}

/*Link to anchors- H1 removed because normali is on top*/
function initialise_anchors(){
  var upper_limit = 2;
  var list = $('#toc').data('bullets') == 'True' ? 'ul' : 'ol';
  var toc = '<' + list + '>';

  $('.wrapper h2,.wrapper h3,.wrapper h4,.wrapper h5,.wrapper h6').each(function(i, heading){
    if($(heading).closest('#toc').length > 0) { return; }

    var header_level = parseInt($(heading).prop("tagName").replace("H",""));

    var anchor;
    if(typeof $(heading).attr('name') !== 'undefined'){
        anchor = $(heading).attr('name');
        $(heading).removeAttr('name');
    } else if(typeof $(heading).attr('id') !== 'undefined'){
        anchor = $(heading).attr('id');
        $(heading).removeAttr('id');
    } else {
        anchor = $(heading).slugify();
    }
    anchor = anchor.replace('"','');

    // Re-anchor to just before the header so the goto link includes the header
    $('<span id="' + anchor + '"></span>').insertBefore($(heading));

    if(upper_limit < header_level){
        toc += '<' + list + '>';
    } else if (upper_limit > header_level) {
        toc += '</li></' + list + '></li>';
    }
    toc += '<li><div><a href="#' + anchor + '">' + $(heading).text() + '</a></div>';
    if(upper_limit === header_level){
        toc += '</li>';
    }
    $(heading).mouseenter(function(){
        if($(heading).children(".headingAnchors").length == 0){
            $(heading).html($(heading).html() + ' <a href="#' + anchor + '" class="headingAnchors" >⚓</a>');
        }
    })
    $(heading).mouseleave(function(){
        $(heading).children(".headingAnchors").remove();
    })
    upper_limit = header_level;
  })
  toc += '</' + list + '>';
  $('#toc').append(toc).show();
}
