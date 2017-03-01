// Rohit Lodha <rohit.lodhartg@gmail.com>
//This file makes use of the jquery.validate.js to validate the upload form of resources before submitting.
$(document).ready(function() {
		console.log("here");
		$("#myForm").validate({
		
	rules:{
		name: "required",
		desc: "required",
		link: {
			required: true,
			url: true
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

