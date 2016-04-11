$(function() {
  function fullscreen() {
    var chat = $('#irchat.full-screen');
    chat.css({
      'width': $(window).width(),
      'height': $(window).height()
    });
    $('iframe', chat).css({
      'height': $(window).height()
    });
    var offset = $('#irchat').offset();
    $('img.fullscreen').css({
      'top': offset.top + 5,
      'left': offset.left + $('#irchat').outerWidth() - 38
    });
  }

  $(window).resize(function() {
    fullscreen();         
  });
  fullscreen();

  $('img.fullscreen').click(function() {
    var chat = $('#irchat');
    if(chat.hasClass('full-screen')) {
        chat.removeClass('full-screen');
        chat.css({'width': '', 'height': ''});
        $('iframe', chat).css({'height': '450px'});
    } else {
        chat.addClass('full-screen');
    }
    fullscreen();
  });
});
