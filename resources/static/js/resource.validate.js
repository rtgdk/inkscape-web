// Rohit Lodha <rohit.lodhartg@gmail.com>
//This file makes use of the jquery.validate.js to validate the upload form of resources before submitting.
$.validator.addMethod('filesize', function (value, element, param) {
    return this.optional(element) || (element.files[0].size<= param*1024)
}, 'File size must be less than {0}');

$(document).ready(function() {
		$("#resourceForm").validate({
		
	rules:{
		name: "required",
		desc: "required",
		link: {
			required: true,
			url: true
		},
		download: {
			filesize: $("#resourceForm").attr('data-quota')
		},
		rendering: {
			filesize: $("#resourceForm").attr('data-quota')
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
		download : "You are exceeding the upload limit: " + $("#resourceForm").attr('data-quota'),
		rendering : "You are exceeding the upload limit: " + $("#resourceForm").attr('data-quota'),
		category:"Please Fill the category",
		license : "Please Fill the License",
		owner : "You must either be the owner or have permission to post this",
		owner_name : "Please Fill the Owner's Name"
	}
});
	var _URL = window.URL || window.webkitURL;
	$("#id_rendering").change(function(e) {
		var file, img;
		if ((file = this.files[0])) {
			var e = document.getElementById('id_category');
			var cat = e.options[e.selectedIndex].innerHTML;
			var sizeMax = e.options[e.selectedIndex].dataset.sizeMax;
			var sizeMin = e.options[e.selectedIndex].dataset.sizeMin;
			var mediax_min = e.options[e.selectedIndex].dataset.media_xMin; 
			var mediax_max = e.options[e.selectedIndex].dataset.media_xMax;
			var mediay_min = e.options[e.selectedIndex].dataset.media_yMin; 
			var mediay_max = e.options[e.selectedIndex].dataset.media_yMax; 
		    img = new Image();
		    img.onload = function() {
		    	if (mediax_min> this.width || this.width > mediax_max){
		        	alert("Image Width Not in range of allowed range for " + cat + ". Allowed width " + mediax_min + "-" + mediax_max +" pixels");
		        	return;
		        	}
		        else if (mediay_min> this.width || this.width > mediay_max){
		        	alert("Image Width Not in range of allowed range for " + cat + ". Allowed width " + mediay_min + "-" + mediay_max +" pixels");
		        	return;
		        	}
		        else if (file.size>sizeMax*1024) {
				alert("Image size above the maximum size allowed for " + cat + " Allowed size : " + sizeMin + "-" +sizeMax +"KB");
				return;
				}
				else if (file.size<sizeMin*1024) {
					alert("Image size below the minimum size allowed for " + cat + " Allowed size : " + sizeMin + "-" +sizeMax +"KB");
					return;
				}
		    };
		    img.onerror = function() {
		        alert( "not a valid file: " + file.type);
		        return;
		    };
		    img.src = _URL.createObjectURL(file);
			
			


		}

	});
	$("#id_download").change(function(e) {
		var file, img;
		if ((file = this.files[0])) {
			var e = document.getElementById('id_category');
			var cat = e.options[e.selectedIndex].innerHTML;
			var sizeMax = (e.options[e.selectedIndex].dataset.sizeMax);
			var sizeMin = (e.options[e.selectedIndex].dataset.sizeMin);
			console.log(file.size);
			console.log(sizeMax);
	        if (file.size>sizeMax*1024) {
			alert("File size above the maximum size allowed for " + cat + ". Allowed size : " + sizeMin + "-" +sizeMax +"KB");
			return;
			}
			else if (file.size<sizeMin*1024) {
				alert("File size below the minimum size allowed for " + cat + ". Allowed size : " + sizeMin + "-" +sizeMax +"KB");
				return;
			}
		}

	});
});

