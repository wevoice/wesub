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

    // Tabs
    $.fn.tabs = function(options){
        var defaults = {};
        
        var opts = $.extend(defaults, options); 

        this.each(function(){
            var $this = $(this);
            
            var $last_active_tab = $($('li.current a', $this).attr('href'));
            $('a', $this).add($('a.link_to_tab')).click(function(){
                var href = $(this).attr('href');
                $last_active_tab.hide();
                $last_active_tab = $(href).show();
                $('li', $this).removeClass('current');
                $('a[href='+href+']', $this).parent('li').addClass('current');
                document.location.hash = href.split('-')[0];
                return false;
            });            
        });
        
        if (document.location.hash){
            var tab_name = document.location.hash.split('-', 1);
            if (tab_name) {
                $('a[href='+tab_name+'-tab]').click();
                document.location.href = document.location.href;
            }
        }
        
        return this;        
    };
});
