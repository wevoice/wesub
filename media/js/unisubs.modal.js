jQuery(document).ready(function($){
	$('a.open-modal').live('click',function(e){
		e.preventDefault();
		target = $(this).attr('href');
		$(target).show();
	});
	$('.modal-header .close', '.bootstrap').click(function(){
        $(this).parents('.modal').hide();
    });
});