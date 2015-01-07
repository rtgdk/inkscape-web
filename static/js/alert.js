
$(document).ready(function() {
  $('.runner').submit(function(){
     jQuery.ajax({
        url: $(this).attr("action"),
        type: 'get',
        success:function(data)
        {
            $('#alert_'+data).remove();
        }, 
     });
    return false;
  });
});

