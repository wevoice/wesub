jQuery(document).ready(function($){
    $('.abbr').each(function(){
        var container = $(this);
        var content = $(this).children('div');
        var oheight = content.css('height', 'auto').height();
        content.css('height','6em');

        $(this).find('.expand').live('click', function(e){
            e.preventDefault();
            if(container.hasClass('collapsed')){
                content.animate({
                    height: oheight
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
    });
});