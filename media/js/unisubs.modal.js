jQuery(document).ready(function($){
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
    $('.action-close', '.bootstrap').click(function(){
        closeModal($(this).parents('.modal'));
        return false;
    });

    function closeModal(e) { 
        e.hide();
        $('body div.well').remove();
        $('html').unbind('click.modal');
    }
});
