/*
 * Copyright 2017, Rohit Lodha <rohit.lodhartg@gmail.com>
 *                 Martin Owens <doctormo@gmail.com>
 *
 * This file is part of the software inkscape-web, consisting of custom 
 * code for the Inkscape project's django-based website.
 *
 * inkscape-web is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * inkscape-web is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with inkscape-web.  If not, see <http://www.gnu.org/licenses/>.
 */

var _URL = window.URL || window.webkitURL;

function humanFileSize(size, scale, def) {
  if(size == undefined) { return def; }
  if(scale) { size = size * scale }
  var i = Math.floor( Math.log(size) / Math.log(1024) );
  return ( size / Math.pow(1024, i) ).toFixed(2) * 1 + ' ' + ['B', 'kB', 'MB', 'GB', 'TB'][i];
};

/* Return true if the value is within the range or the range doesn't exist */
function range(minimum, maximum, value) {
  return value == undefined || (
         (minimum == undefined || value >= minimum)
      && (maximum == undefined || value <= maximum))
}

//This file makes use of the jquery.validate.js to validate the upload form of resources before submitting.
$.validator.addMethod('quota', function (value, element, param) {
  return this.optional(element) || ($(element).data('size') <= param)
}, function(param, element) {
  var quota = humanFileSize(param);
  var size = humanFileSize($(element).data('size'));
  return $.validator.format('File size ({0}) must be less than your remaining quota: {1}', size, quota);
});

$.validator.addMethod('is_image', function (value, element, param) {
  return this.optional(element) || $(element).data('isimage');
}, 'This file must be an image.');

$.validator.addMethod('category_size', function (value, element, param) {
    var cat = $(param).find(":selected");
    var in_range = range(cat.data('size-min'), cat.data('size-max'), $(element).data('size') / 1024);
    return this.optional(element) || in_range;
}, function (param, element) {
    var cat = $(param).find(":selected");
    var quota = humanFileSize($("#resourceForm").data('quota'));
    return $.validator.format("This categories requires files to between {0} and {1}",
        humanFileSize(cat.data('size-min'), 1024, '0B'),
        humanFileSize(cat.data('size-max'), 1024, quota)
    );
});

$.validator.addMethod('category_area', function (value, element, param) {
    var cat = $(param).find(":selected");
    console.log($(element).data());
    var in_range =
         range(cat.data('media_x-min'), cat.data('media_x-max'), $(element).data('media_x'))
      && range(cat.data('media_y-min'), cat.data('media_y-max'), $(element).data('media_y'));
    return this.optional(element) || in_range;
}, function(param, element) {
    var cat = $(param).find(":selected");
    return $.validator.format('This category requires images to be {0}-{1} wide and {2}-{3} high.',
        cat.data('media_x-min') || 0,
        cat.data('media_x-max') || 'Any',
        cat.data('media_y-min') || 0,
        cat.data('media_y-max') || 'Any',
    );
});

$.validator.addMethod('category_type', function (value, element, param) {
    var types = $(param).find(":selected").data('types');
    var is_type = types == undefined || types.split(',').indexOf($(element).data('type')) > -1;
    return this.optional(element) || is_type;
}, function(param, element) {
    var types = $(param).find(":selected").data('types');
    return 'This category requires file to be one of these types: ' + types
}); 

$(document).ready(function() {
  $("input[type='file']").change(save_file_details);
  var link_mode = $('.linker').length > 0;
  var paste_mode = $('.paster').length > 0;
  // TODO: paste_mode uses area size min and max to set
  // how large the text must be in lines x words. We should
  // validate that.

  $("#resourceForm").validate({
    ignore: "", // validate invisible inputs
    rules:{
      name: "required",
      link: {
        required: link_mode,
        url: true
      },
      download: {
        required: !link_mode,
        quota: !paste_mode && $("#resourceForm").data('quota'),
        category_size: !paste_mode && '#id_category',
        category_area: !paste_mode && '#id_category',
        category_type: !paste_mode && '#id_category',
      },
      rendering: {
        quota: $("#resourceForm").data('quota'),
        is_image: true,
      },
      category : "required",
      license : "required",
      owner : "required",
      owner_name : {
        required: function(element) {
          return $("#id_owner").val()=="False";
        }
      }
    },
    messages:{
      name: "Please Fill the resource name",
      desc: "Please Fill the Description",
      link: "Please Fill the Link",
      category:"Please Fill the category",
      license : "Please Fill the License",
      owner : "You must either be the owner or have permission to post this",
      owner_name : "Please Fill the Owner's Name"
    }
  });
});

/* generic function to record file upload information in jquery data */
function save_file_details(e) {
  var input = $(this);
  var file = this.files[0];
  if (file) {
    input.data('size', file.size);
    input.data('type', file.type);
    var img = new Image();
    img.onload = function() {
      input.data('isimage', true);
      input.data('media_x', this.width);
      input.data('media_y', this.height);
    }
    img.onerror = function() {
      input.data('isimage', false);
    };
    img.src = _URL.createObjectURL(file);
  }
}

