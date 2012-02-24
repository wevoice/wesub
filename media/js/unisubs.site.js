var Site = function() {

    this.init = function() {

        // Global cached jQuery objects
        this.$html = $('html');
        this.$body = $('html');

        // Base JS (any page that extends base.html)
        if (this.$html.hasClass('base')) {
            this.Views['base']();
        }

        // Page specific JS
        if (this.$html.attr('id')) {
            this.Views[this.$html.attr('id')]();
        }
    };

    this.Views = {
        base: function() {

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

            // CSRF Header
            function addCSRFHeader($){
                /* Django will guard against csrf even on XHR requests, so we need to read
                   the value from the cookie and add the header for it */
                $.ajaxSetup({
                    beforeSend: function(xhr, settings) {
                        function getCookie(name) {
                            var cookieValue = null;
                            if (document.cookie && document.cookie !== '') {
                                var cookies = document.cookie.split(';');
                                for (var i = 0; i < cookies.length; i++) {
                                    var cookie = jQuery.trim(cookies[i]);
                                    // Does this cookie string begin with the name we want?
                                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                        break;
                                    }
                                }
                            }
                            return cookieValue;
                        }
                        if (!((/^http:.*/).test(settings.url) || (/^https:.*/).test(settings.url))) {
                            // Only send the token to relative URLs i.e. locally.
                            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                        }
                    }
                });
            }

            // jQuery soup to someday be cleaned up
            (function() {
                $('#closeBut').click(function(){
                    $('#messages').remove();
                    return false;
                });
                $('li.search input').keypress(function(e) {
                    if ((e.which && e.which == 13) || (e.keyCode && e.keyCode == 13)) {
                        $('li.search form').submit();
                        return false;
                    }
                    else
                        return true;
                });
                jQuery.Rpc.on('exception', function(e){
                    jQuery.jGrowl.error(e.message);
                });
            })();
            

            window.usStartTime = (new Date()).getTime();
            window.addCSRFHeader = addCSRFHeader;
            addCSRFHeader($);
        },
        home: function() {

        }
    };
};

$(function() {
    window.Site = new Site();
    window.Site.init();
});
