// Rohit Lodha <rohit.lodhartg@gmail.com>
//This file makes use of the jquery.validate.js to validate the upload form of resources before submitting.
$.validator.addMethod('filesize', function (value, element, param) {
    return this.optional(element) || (element.files[0].size <= param)
}, 'File size must be less than {0}');

$(document).ready(function() {
		$("#myForm").validate({
		
	rules:{
		name: "required",
		desc: "required",
		link: {
			required: true,
			url: true
		},
		download: {
			filesize: $("#myForm").attr('data-quota')
		},
		rendering: {
			filesize: $("#myForm").attr('data-quota')
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
		download : "You are exceeding the upload limit: " + $("#myForm").attr('data-quota'),
		rendering : "You are exceeding the upload limit: " + $("#myForm").attr('data-quota'),
		category:"Please Fill the category",
		license : "Please Fill the License",
		owner : "You must either be the owner or have permission to post this",
		owner_name : "Please Fill the Owner's Name"
	}
});
});

