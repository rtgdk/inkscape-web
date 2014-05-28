/*
 * Copyright (c) Martin Owens 2014
 *
 * License: AGPLv3
 *
 * Consult the README for the inkscape-web project for full license details.
 */

var max_size = 3000000; // 3MB file limit on previews

function addEventHandler(obj, evt, handler) {
  if(obj.addEventListener) { // W3C Method
    obj.addEventListener(evt, handler, false);
  } else if(obj.attachEvent) { // Internet Explorer
    obj.attachEvent('on'+evt, handler);
  } else { // Catch all
    obj['on'+evt] = handler;
  }
}

function get_mime_icon(mimeid) {
  var mime = mimeid.split("/");
  if(['image'].indexOf(mime[0]) >= 0) { return mime[0]; }
  if(mime[1].endsWith('ml')) { return 'xml'; }
  if(mime[1].indexOf('zip') >= 0) { return 'archive'; }
  if(mime[1].indexOf('compressed') >= 0) { return 'archive'; }
  if(['x-tar'].indexOf(mime[1]) >= 0) { return 'archive'; }
  if(['text','application'].indexOf(mime[0]) >= 0) { return mime[1]; }
  return mime[0];
};

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
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

String.prototype.endsWith = function(suffix) {
  return this.indexOf(suffix, this.length - suffix.length) !== -1;
};


function registerDropZone(drop_id, gallery_id, post_url, media_url) {

  var drop    = document.getElementById(drop_id);
  var gallery = document.getElementById(gallery_id);

  if(window.FileReader) { 

  addEventHandler(window, 'load', function() {
    function cancel(e) {
      if (e.preventDefault) { e.preventDefault(); }
      return false;
    }
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
          var item = document.createElement("div");
          item.setAttribute('class', 'galleryitem');
          var link = document.createElement("a");
          link.setAttribute('class', 'link');

          var img = document.createElement("img"); 
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
          img.setAttribute('title', "New Upload: "+file)

          var p = document.createElement("p");
          p.setAttribute('class', 'new');
          var progress = document.createElement("progress");
          progress.getAttribute('min', 0);
          progress.getAttribute('max', file.size);
          p.appendChild(progress);

          link.appendChild(img);
          item.appendChild(link);
          item.appendChild(p);
          gallery.appendChild(item);

          var formData = new FormData();
          formData.append('download', file);
          formData.append('name', file.name);
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
              if (xhr.responseText.indexOf('OK') >= 0) {
                p.innerHTML = '<a>'+file.name+'</a>';
              } else {
                p.innerHTML = '<a>'+xhr.responseText+'</a>';
              }
            } else {
              document.write(xhr.responseText);
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

