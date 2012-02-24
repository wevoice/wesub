$(function() {

    // Abbr
    if ($('.abbr').length) {
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
    }

    // Filters
    if ($('#sort-filter').length) {
        $('#sort-filter').click(function(e) {
            e.preventDefault();

            $('.filters').toggle();
            
            $(this).children('span').toggleClass('open');
        });

        $('select', '.filters').change(function(e) {
            window.location = $(this).children('option:selected').attr('value');
        });
    }

    // Modal
    if ($('a.open-modal').length) {
        $('a.open-modal').live('click',function(e){
            e.preventDefault();
            $target = $($(this).attr('href'));
            $target.show();

            $('body').append('<div class="well"></div>');

            $target.click(function(event){
                event.stopPropagation();
            });
            $('html').bind('click.modal', function() {
                closeModal($target);
            });
        });
        $('.action-close, .close', '.bootstrap').click(function(){
            closeModal($(this).parents('.modal'));
            return false;
        });

        function closeModal(e) { 
            e.hide();
            $('body div.well').remove();
            $('html').unbind('click.modal');
        }
    }

});
