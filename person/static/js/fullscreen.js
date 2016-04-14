$(function() {
  function fullscreen() {
    var x_pad = 4;
    var y_pad = 4;
    var chat = $('#irchat.full-screen');
    chat.css({
      'width': $(window).width() - (x_pad * 2),
      'height': $(window).height() - (y_pad * 4)
    });
    $('iframe', chat).css({
      'height': $(window).height() - (y_pad * 2)
    });
    var offset = $('#irchat').offset();
    if(chat.length > 0) {
      $('img.fullscreen').css({
        'top': offset.top,
        'left': offset.left + $('#irchat').outerWidth() - 32 - (x_pad * 2)
      });
    } else {
      $('img.fullscreen').css({
        'top': offset.top + y_pad,
        'left': offset.left + $('#irchat').outerWidth() - 32 - x_pad
      });
    }
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
