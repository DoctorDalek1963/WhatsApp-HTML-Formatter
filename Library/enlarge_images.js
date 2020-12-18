$(function () {
    $('img').on('click', function() {
        if ($(this).hasClass('small')) {
            $(this).removeClass('small').addClass('large');
            $(this).animate({'max-height': '40vw', 'max-width': '80vw'}, 200);
        } else {
            $(this).removeClass('large').addClass('small');
            $(this).animate({'max-height': '400px', 'max-width': '800px', 'width': 'auto'}, 200);
        }
    });
});
