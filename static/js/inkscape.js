/* Page loading processes */
$(document).ready(function() {
  if($("#menu"))menu();
  if($('[class|="maxHeight"]')[0])maxHeight();
  if($("#toplogin"))adjustBar();
  if($("#shield .tabs"))furnishTabs();
});

/* Front page code for tabs */
var currentTab = null;
function onOff(e) {
  e.toggleClass('current');
  var b = $("#shield #banners > div").get(e.index());
  $(b).toggleClass('current', e.hasClass('current'));
}
function selectBanner() {
  if(currentTab) onOff(currentTab);
  currentTab = $(this).parent();
  onOff(currentTab);
}
function furnishTabs() {
  $("#shield > .tabs").children("li").each(function(){
    $(this).children("a:first-child").mouseover(selectBanner);
    $(this).children("a:first-child").click(selectBanner);
  });
  currentTab = $("#shield > .tabs li.current");
}

function getPng(t) {
  if(t.src.slice(-3)=='svg') {
    t.src = t.src.slice(0,-3) + "png";
  }
}

/* == PopUp implimentation == */
function popUp(title, msg, href, cancel, ok) {
    if(document.getElementById('blanket')) {
      $('#blanket').remove();
      $('#popup').remove();
    } else if(title) {
      $('body').append( "<div id='blanket'/>" );
      $('#blanket').click(popUp); // Cancel when clicking outside
      $('body').append( "<div id='popup'/>" );
      $('#popup').append( "<h1>" + title + "</h1>" ).append( "<p>" + msg + "</p>" )
                 .append( "<form class='buttons' action='"+href+"' method='POST'/>");
      $('#popup .buttons').append("<input type='hidden' name='csrfmiddlewaretoken' value='"+getCookie('csrftoken')+"'/>")
                          .append("<button class='start'>" + cancel + "</button>")
                          .append("<button type='submit' class='end unique' name='confirm'>" + ok + "</button>");
      $('#popup .buttons .start').click(popUp);
      $('#popup').css({
        'top': 'calc(50% - ' + ($('#popup').innerHeight() / 2) + 'px)',
        'left': 'calc(50% - ' + ($('#popup').innerWidth() / 2) + 'px)',
      });
    } else {
      return true;
    }
    return false;
}
function popUpLink(msg, cancel, ok) {
  // Allows a link to fail gracefully.
  var a = document.currentScript.previousElementSibling;
  $( document ).ready( function() {
    var href = a.href;
    a.onclick = function() { return popUp(a.title, msg, href, cancel, ok); };
    a.href = '#nowhere'
  });
}
/* End popup */

jQuery.fn.getMaxHeight = function(){
    var ca = this.attr('class');
    var rval = [];
    if(ca && ca.length && ca.split){
        ca = jQuery.trim(ca); /* strip leading and trailing spaces */
        ca = ca.replace(/\s+/g,' '); /* remove doube spaces */
        var n = ca.indexOf("maxHeight-"); 
        ca.substring(n);
        rval = ca.split(' ');
    }
    return rval[0].replace("maxHeight-","");
}

function menu(){
    var elementHeight=$("#menu").children("li:first-child").height();
    var containerHeight=$("#menu").height();
    var i = 0;
    var onePixelLess = parseInt( $("#menu").children("li").children("a:first-child").css('font-size'))-1 + "px";
    while(containerHeight > elementHeight){
        $("#menu").children("li").each(function(){
            var a = $(this).children("a:first-child");
            a.css('font-size',onePixelLess);
            a.css('padding-left',parseInt(a.css('padding-left'))-1 + "px");
            a.css('padding-right',parseInt(a.css('padding-right'))-1 + "px");
            elementHeight = $(this).height();
        })
        i++;
        containerHeight = $("#menu").height();
    }
}

function adjustBar(){
    var tw = parseInt( $("#toplogin").width() );
    var fw = parseInt( $("#toplogin").children(".topdrop").width() );
    $("#toplogin").children(".topdrop").css('margin-left', (tw-fw-20)+"px");
}

function maxHeight(){
    $('[class|="maxHeight"]').each(function(){
        var elementHeight = $(this).height();
        var containerHeight=$(this).getMaxHeight();
        var textSize;
        var i = 0;
        while(containerHeight < elementHeight){
            textSize =  parseInt($(this).css('font-size'));
            if(textSize == 5) break;
           if(i != 0){
                $(this).css('font-size',textSize-1 + "px");
            }
            i++;
            elementHeight = $(this).height();
        }
    })
}
