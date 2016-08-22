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
  if($("#menu"))menu();
  if($('[class|="maxHeight"]')[0])maxHeight();
  if($("#shield .tabs"))furnishTabs();
  if($(".inlinepages"))inlinePages();
  $("#tab_user input").focus(true, focused);
  $("#tab_user input").focusout(false, focused);
  $("[src$='.svg']").error(onSvgError);
  $(".image.only img").error(iconInstead);
  $(".dotdotdot").click(paginator_expand);
  $(".ellipses-button").click(ellipses);
  $(".ellipses-button").show();
  $(".modal-dialog .tab").click(modalfieldsets);
  $(".modal-dialog .fields").hide();
  $(".modal-dialog .tab:first-child").click();
  close_elements();
  adjustBar();
});

function modalfieldsets(event) {
  var target = $(this);
  var previous = $('.tab.selected', target.parent);
  if(target && target != previous) {
    if(previous) {
      previous.removeClass('selected');
      var fields = $('#' + previous.attr('for'));
      fields.hide();
    }
    target.addClass('selected');
    var fields = $('#' + target.attr('for'));
    fields.show();
  }
}

function ellipses(event) {
  var target = $(this).parent();
  if(target.hasClass('ellipses-hidden')) {
    target.removeClass('ellipses-hidden');
    target.addClass('ellipses-shown');
    $(this).hide();
  } else if(target.hasClass('ellipses-shown')) {
    target.removeClass('ellipses-shown');
    target.addClass('ellipses-hidden');
    $(this).show();
  }
}

function paginator_expand(event) {
  // On clicking ... in a paginator, this js will expand it
  var a = parseInt($(this).prev().text());
  var b = parseInt($(this).next().text());
  $(this).attr('href', $(this).attr('data-href'));
  $(this).removeAttr('data-href');
  var template = this.outerHTML;
  for (var i = a + 1; i < b; i++) {
      var html = template.replace(/\.\.\./g, i);
      $(html).insertBefore($(this));
  }
  $(this).hide();
  return false;
}

function iconInstead(event) {
  this.src = $(this).data('icon');
}

function onSvgError(event) {
  if(this.src.slice(-3)=='svg' && !$(this).data('static')) {
    this.src = this.src.slice(0,-3) + "png";
  }
}

function close_elements() {
  $("#messages li").each(function() {
    $(this).prepend("<span class='x-close'>x</span>");
  });
  $(".x-close").each(function() {
    $(this).click(function() {
      $(this).parent().remove();
    });
  });
}

function focused(unhide) {
  var target = $( this ).closest("li");
  // This delay is needed because unfocus will kill the tab-next process
  // before the next item can re-focus the list item target.
  setTimeout( function () { target.toggleClass('focused', unhide.data); }, 100);
}

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      var cookieName = cookie.substring(0, name.length + 1);
      if (cookieName == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

/* Front page code for tabs */
var currentTab = null;
function onOff(e) {
  e.toggleClass('current');
  var b = $("#shield #banners > div").get(e.index());
  $(b).toggleClass('current', e.hasClass('current'));
}
function selectBanner(nextTab) {
  if(currentTab) onOff(currentTab);
  currentTab = nextTab;
  onOff(currentTab);
}
function selectBannerNow() {
  if($(this).hasClass('current')) $("#shield .tabs").toggleClass('expanded');
  selectBanner($(this));
  return false;
}
function selectBannerSoon() {
  // We create a timer for the mouse over event,
  // If the mouse leaves before the timeout is done, it's canceled.
  var nextTab = $(this);
  this.sb_timer = setTimeout( function () { selectBanner(nextTab) }, 100);
}
function cancelBanner() {
  if(this.sb_timer) { clearTimeout(this.sb_timer) }
}
function furnishTabs() {
  $("#shield > .tabs").children("li")
    .mouseover(selectBannerSoon).mouseout(cancelBanner).click(selectBannerNow);
  currentTab = $("#shield > .tabs li.current");
}

function inlinePages() {
  $(".inlinepages > .tabs").children("li").each(function(){
    $(this).click(selectInlinePage);
  });
  $(".inlinepages > .tabs > li:first-child").trigger("click");
}
function selectInlinePage() {
  $(".inlinepages .selected").each(function(){
    $(this).toggleClass('selected', 'false');
  });
  $(this).toggleClass('selected', true)
  $("#"+this.id+"-page").toggleClass('selected', true)
}

/* == PopUp implimentation == */
function popUp(title, msg, href, cancel, ok, next) {
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
                          .append("<a class='btn btn-cancel'>" + cancel + "</a>");
      if(next){
        $('#popup .buttons').append("<input type='hidden' name='next' value='"+next+"'/>");
      }  
      $('#popup .buttons').append("<button type='submit' class='btn btn-primary' name='confirm' value='true'>" + ok + "</button>");
      $('#popup .buttons .btn-cancel').click(popUp);
      $('#popup').css({
        'top': 'calc(50% - ' + ($('#popup').innerHeight() / 2) + 'px)',
        'left': 'calc(50% - ' + ($('#popup').innerWidth() / 2) + 'px)',
      });
    } else {
      alert("No title specified!");
      return true;
    }
    return false;
}
function popUpLink(msg, cancel, ok, next) {
  // Allows a link to fail gracefully.
  var a = document.currentScript.previousElementSibling;
  $( document ).ready( function() {
    var href = a.href;
    $(a).click( function() { return popUp(a.title, msg, href, cancel, ok, next); } );
    a.href = '#nowhere'
  });
}
/* End popup */

jQuery.fn.getMaxHeight = function(){
    var ca = this.attr('class');
    var rval = [];
    if(ca && ca.length && ca.split) {
        ca = jQuery.trim(ca); /* strip leading and trailing spaces */
        ca = ca.replace(/\s+/g,' '); /* remove doube spaces */
        var n = ca.indexOf("maxHeight-"); 
        ca.substring(n);
        rval = ca.split(' ');
    }
    return rval[0].replace("maxHeight-","");
}

function menu(){
    $("#menu-toggle").click(function(){ $("#menu").slideToggle(); });
    if(screen.width < 960) {
        $("#menu > li").each(function(){
            var ancestorDuplicate = $("<li>").addClass('children').append($(this).children("a").clone());
            if($(this).hasClass('selected')) ancestorDuplicate.addClass('selected');
            $(this).children("ul").prepend(ancestorDuplicate);
            $(this).children("a").click(function(){
                $(this).parent().toggleClass('activated');
                return false;
            });
            $(this).mouseleave(function(){
                $(this).removeClass('activated');
            });
        });
    } else {
        var itemHeight = $("#menu > li").height();
        var menuHeight = $("#menu").height();
        var fontSize = parseInt($("#menu > li > a").css('font-size'));
        var minFontSize = 12;
        var initialPadding = parseInt($("#menu > li > a").css('padding-left'));
        var paddingSize = initialPadding;
        var minPaddingSize = paddingSize * 0.7;
        while(menuHeight > itemHeight && (paddingSize > minPaddingSize || fontSize > minFontSize)) {
            paddingSize--;
            if(paddingSize < minPaddingSize && fontSize > minFontSize) {
                fontSize--;
                paddingSize = initialPadding;
                minPaddingSize *= 0.7;
            }
            $("#menu > li > a").css({
                'font-size': fontSize + "px",
                'padding-left': paddingSize + "px",
                'padding-right': paddingSize + "px"});
            menuHeight = $("#menu").height();
        }
        if (paddingSize <= minPaddingSize && fontSize <= minFontSize) {
            $(".header .nav").css('height', 'auto');
            $("#menu").css({ 'display': 'table', 'table-layout': 'fixed' });
            $("#menu > li").css({ 'display': 'table-cell', 'float': 'none', 'vertical-align': 'top' });
            $("#menu > li > a")
                .css({ 'display': 'table-cell', 'padding': '8px ' + paddingSize + 'px', 'vertical-align': 'middle' })
                .css('height', $("#menu > li > a").height());
        }
    }
}

function adjustBar() {
    $("#tabs > li.dropdown").each(function() {
        var tab_width = parseInt($(this).width());
        var drop_width = parseInt($(this).children("div").width());
        $(this).children("div").css('margin-left', (tab_width - drop_width)+"px");
    });
}

function maxHeight(){
    $('[class|="maxHeight"]').each(function(){
        var elementHeight = $(this).height();
        var containerHeight=$(this).getMaxHeight();
        var textSize;
        var i = 0;
        while(containerHeight < elementHeight && i < 100){
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

function reply_message(msg_id) {
    var f = document.getElementById('form-'+msg_id);
    f.setAttribute('onsubmit','');
    f.setAttribute('method','post');
    document.getElementById('body-'+msg_id).setAttribute('style','');
    return false;
}

