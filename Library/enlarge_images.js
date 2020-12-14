$('img').click(function() {
    if ($(this).hasClass('small')) {
        $(this).removeClass('small').addClass('large');
    } else {
        $(this).removeClass('large').addClass('small');
    }
});
