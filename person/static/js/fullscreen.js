$(function() {
  function fullscreen() {
    $('html, body').css({
      'overflow':'hidden'
    })
    var chat = $('#irchat.full-screen');
    chat.css({
      'width': $(window).width(),
      'height': $(window).height()
    });

    $('iframe', chat).css({
      'height': $(window).height()
    });
  }

  $(window).resize(function() {
    fullscreen();         
  });

  $('img.fullscreen').click(function() {
    var chat = $('#irchat');
    if(chat.hasClass('full-screen')) {
        chat.removeClass('full-screen');
        chat.css({'width': '', 'height': ''});
        $('iframe', chat).css({'height': '450px'});
        $('html, body').css({
          'overflow':'hidden'
        })
    } else {
        chat.addClass('full-screen');
    }
    fullscreen();
  });
});
