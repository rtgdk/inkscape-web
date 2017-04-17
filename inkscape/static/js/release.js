/*
* Copyright 2017,  Rohit Lodha <rohit.lodhartg@gmail.com>
* This file is for changing the mouse click action on release shield tabs.
* It overwrites the default function of inkscape.js without affecting home shield tabs.
*/
$(document).ready(function() {
  furnishShieldTabs();
});

function selectBanner(nextTab) {
  $("#shield .current").removeClass('current');
  nextTab.addClass('current');
  $("#shield #banners > div").eq(nextTab.index()).addClass('current');
}
function furnishShieldTabs() {
  $("#shield > .tabs").children("li")
    .mouseover(function() {
      var nextTab = $(this);
      this.sb_timer = setTimeout(function() { selectBanner(nextTab); }, 100);
    })
    .mouseout(function() {
      if(this.sb_timer) clearTimeout(this.sb_timer);
    });
  currentTab = $("#shield > .tabs li.current");
}


