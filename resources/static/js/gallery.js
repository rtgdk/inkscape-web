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

var max_size = 3000000; // 3MB file limit on previews
var debug = true;

$(document).ready(function() {
  var elem = $('.upload #id_download');
  elem.addClass('hidden');
  $('.image.uploader label').show();
  lbl = $('.image.uploader label p');
  img = $('.image.uploader label img');
  img.error(function(e) {
      if(img.data('static')) {
          target = img.data('static') + 'mime/unknown.svg';
          if(this.src != target) { this.src = target; }
          return false;
      }
  });

  elem.on('change', function() {
    if (this.files && this.files[0]) {
      var file = this.files[0];
      var icon = get_mime_icon(file.type);

      if (icon == 'image' && file.size < max_size) {
        // File Reader allows us to show a preview image
        var reader = new FileReader();
        reader.onload = function (e) {
            img.attr('src', e.target.result);
        }
        reader.readAsDataURL(file);
      } else {
        img.attr('src', img.data('static') + 'mime/' + icon + '.svg');
      }
      lbl.html(file.name);
    }
  });

  $('select[data-filter_by]').each(function() {
    var target = $(this);
    var filters = [];

    $('option', target).each(function() {
        // Record all filters into one list for counter test
        var filter = $(this).data('filter');
        if(filter != undefined) {
            filters = filters.concat(filter);
        }
    });

    var filter_by = $('#' + target.data('filter_by'));
    $('option', filter_by).each(function() {
        // Disble any counter options with no filters, this should
        // Warn admins that their license selection isn't working.
        var val = parseInt($(this).attr('value'));
        if(!isNaN(val) && filters.indexOf(val) == -1) {
            $(this).attr("disabled", "true");
        }
    });

    filter_by.change(function() {
      // Disable any options not suitable/filtered out.
      if($(this).val()) {
        target.removeAttr("disabled");
      } else {
        target.attr("disabled", "true");
      }
      var val = parseInt($(this).val());
      $('option', target).each(function() {
          var filter = $(this).data('filter');
          if(filter != undefined) {
            if(filter.indexOf(val) >= 0) {
              $(this).removeAttr("disabled");
            } else {
              $(this).attr("disabled", "true");
              $(this).removeAttr("selected");
            }
          }
      });
    }).change();
  });
});

function addEventHandler(obj, evt, handler) {
  if(obj.addEventListener) { // W3C Method
    obj.addEventListener(evt, handler, false);
  } else if(obj.attachEvent) { // Internet Explorer
    obj.attachEvent('on'+evt, handler);
  } else { // Catch all
    obj['on'+evt] = handler;
  }
};

function get_mime_icon(mimeid) {
  if(!mimeid){ mimeid = "text/plain"; }
  var mime = mimeid.split("/");
  if(['image'].indexOf(mime[0]) >= 0) { return mime[0]; }
  if(mime[1].endsWith('ml')) { return 'xml'; }
  if(mime[1].indexOf('zip') >= 0) { return 'archive'; }
  if(mime[1].indexOf('compressed') >= 0) { return 'archive'; }
  if(['x-tar'].indexOf(mime[1]) >= 0) { return 'archive'; }
  if(['text','application'].indexOf(mime[0]) >= 0) { return mime[1]; }
  return mime[0];
};


Function.prototype.bindToEventHandler = function bindToEventHandler() {
  var handler = this;
  var boundParameters = Array.prototype.slice.call(arguments);
  //create closure
  return function(e) {
    e = e || window.event; // get window.event if e argument missing (in IE)   
    boundParameters.unshift(e);
    handler.apply(this, boundParameters);
  }
};
function appendElement(par, type, props, content) {
  var ele = document.createElement(type);
  if(props) {
    Object.keys(props).forEach(function (key) {
      ele.setAttribute(key, props[key]);
    });
  }
  if(content) { ele.innerHTML = content; }
  if(par) { par.appendChild(ele); }
  return ele;
}
function prependElement(par, type, props, content) {
  var ele = appendElement(null, type, props, content);
  par.insertBefore(ele, par.firstChild);
  return ele;
}


String.prototype.endsWith = function(suffix) {
  return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

function cancel(e) {
  if (e.preventDefault) { e.preventDefault(); }
  return false;
};


function registerDropZone(drop_id, gallery_id, post_url, media_url, keep) {
 if(keep==undefined){ keep=true; }
 if(window.FileReader) { 
  addEventHandler(window, 'load', function() {
    var drop    = document.getElementById(drop_id);
    var gallery = document.getElementById(gallery_id);

    // Tells the browser that we *can* drop on this target
    addEventHandler(drop, 'dragover', cancel);
    addEventHandler(drop, 'dragenter', cancel);

    addEventHandler(drop, 'drop', function (e) {
      e = e || window.event; // get window.event if e argument missing (in IE)   
      if (e.preventDefault) { e.preventDefault(); } // stops the browser from redirecting off to the image.

      var dt    = e.dataTransfer;
      var files = dt.files;
      for (var i=0; i<files.length; i++) {
        var file = files[i];
        var reader = new FileReader();
      
        addEventHandler(reader, 'loadend', function(e, file) {
          var item = prependElement(gallery, "div",      {'class':'galleryitem'});
          var link = appendElement(item,     'a',        {'class':'link'});
          var img  = appendElement(link,     'img',      {'title':"New Upload: "+file});
          var p    = appendElement(item,     'p',        {'class':'new'});
          var progress = appendElement(p,    'progress', {'min':0, 'max':file.size});

          addEventHandler(img, 'error', function(e) {
            target = media_url + 'mime/unknown.svg';
            if(this.src != target) { this.src = target; }
          });
          img.file = file;
          var icon = get_mime_icon(file.type);
          if (icon == 'image' && file.size < max_size) {
              img.src = this.result;
          } else {
              img.src = media_url + 'mime/' + icon + '.svg';
          }

          // Put the drop back where is was
          if(drop.parentNode.parentNode == gallery) {
            gallery.insertBefore(drop.parentNode, gallery.firstChild);
          }

          var formData = new FormData();
          formData.append('download', file);
          formData.append('name', "$"+file.name);
          formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));

          var xhr = new XMLHttpRequest();
          xhr.open('POST', post_url);

          xhr.upload.onprogress = function (event) {
            if (event.lengthComputable) {
              progress.value = event.loaded;
            }
          };

          xhr.onload = function () {
            if (xhr.status === 200) {
              if (xhr.responseText.slice(0,2) == 'OK') {
                if(!keep) {
                  item.parentNode.removeChild(item);
                } else {
                  temp = document.createElement('div');
                  temp.innerHTML = xhr.responseText.slice(3)
                  item.parentNode.replaceChild(temp.children[0], item);
                }
              } else {
                p.innerHTML = '<a>FAILED</a>';
                err = document.getElementById('errors')
                err.innerHTML = xhr.responseText;
                err.setAttribute('class','errors');
              }
            } else if(debug) {
              document.write(xhr.responseText);
            } else {
              p.innerHTML = '<a title="'+xhr.status+'">ERROR ' + xhr.status + "!</a>";
            }
          };
          xhr.send(formData);
        }.bindToEventHandler(file));
        reader.readAsDataURL(file);
      }
      return false;
    });
  });
}

}

 /* Guides sometimes show a status saying "your browser doesn't support this"
  * but I reckon the html should assume non-support and the javascript should
  * modify that as needed. Thus noscript and nofeature is covered. 
  */

