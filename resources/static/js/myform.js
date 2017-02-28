
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
		owner : "Please Fill the Permission",
		owner_name : "Please Fill the Owner's Name"
	}
});
});

