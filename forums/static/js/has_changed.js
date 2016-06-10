/*
 * Provides a way for javascript to show if links have changed since the last visit.
 */

$(document).ready(function() {
  $(".changes").each(function() {
    primary_key = 'changed-' + $(this).data('pk');
    localStorage.setItem(primary_key, +new Date);
  });
  $(".unchanged").each(function() {
    var target = $(this);
    var primary_key = 'changed-' + target.data('pk');
    var changed = new Date(target.data('changed'));

    if(!changed || !target.data('pk')) {
      return;
    }
    var timestamp = localStorage.getItem(primary_key);
    var lastvisit = new Date(parseInt(timestamp));

    if (!timestamp || changed > lastvisit) {
        target.removeClass("unchanged");
        target.addClass("changed");
    }
  });
});
