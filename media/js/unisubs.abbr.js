jQuery(document).ready(function($){
    $('.abbr').each(function(){
        var container = $(this);
        var content = $(this).children('.abbr-content');
        var orig_height = content.height();

        if(orig_height > 72) {
            $(this).addClass('collapsed').append('<a class="expand" href="#">Show all ↓</a>');

            $(this).find('.expand').live('click', function(){
                if(container.hasClass('collapsed')){
                    content.animate({
                        height: orig_height
                    }, 'fast');
                    $(this).text('Collapse ↑');
                } else {
                    content.animate({
                        height: '6em'
                    }, 'fast');
                    $(this).text('Show all ↓');
                }
                container.toggleClass('collapsed expanded');
            });
        }
    });
});