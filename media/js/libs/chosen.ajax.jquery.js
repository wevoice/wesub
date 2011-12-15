(function() {
    (function($) {
        return $.fn.ajaxChosen = function(options, callback) {
            var select;
            select = this;
            this.chosen();
            return this.next('.chzn-container').find(".chzn-search > input").bind('keyup', function() {
                var field, val;
                val = $.trim($(this).attr('value'));
                if (val === $(this).data('prevVal')) {
                    return false;
                }
                if (val.length < 1) {
                    $sel = $('ul.chzn-results', select.next('.chzn-container'));
                    $lis = $sel.children('li');

                    if ($lis.length === 1) {
                        $sel.children('li').remove();
                        $sel.append($('<li class="no-results">Begin typing to search.</li>'));
                    }
                    return false;
                }
                $(this).data('prevVal', val);
                field = $(this);
                options.data = {
                    term: val
                };
                if (typeof success !== "undefined" && success !== null) {
                    success;
                } else {
                    success = options.success;
                };
                options.success = function(data) {
                    var items;
                    if (!(data != null)) {
                        return;
                    }
                    select.find('option').each(function() {
                        if (!$(this).is(":selected")) {
                            return $(this).remove();
                        }
                    });
                    items = callback(data);
                    $.each(items, function(value, text) {
                        return $("<option />", {'value': value, 'html': text}).appendTo(select);
                    });
                    var rem = field.attr('value');
                    select.trigger("liszt:updated");
                    field.attr('value', rem);

                    field.keyup();

                    if (typeof success !== "undefined" && success !== null) {
                        return success();
                    }
                };
                return $.ajax(options);
            });
        };
    })(jQuery);
}).call(this);
