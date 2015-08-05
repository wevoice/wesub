/* Amara, universalsubtitles.org
 *
 * Copyright (C) 2015 Participatory Culture Foundation
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see
 * http://www.gnu.org/licenses/agpl-3.0.html.
 */
(function() {

var $document = $(document);

$.fn.autocompleteTextbox = function(options) {
    this.each(function() {
        var field = $(this);
        var autocompleteList = $('<ul class="autocomplete">');
        var lastValue = null;
        var settings = $.extend({
            // default options
            queryParamName: 'query',
            url: field.data('autocompleteUrl'),
            extraFields: field.data('autocompleteExtraFields')
        }, options);

        autocompleteList.appendTo(field.closest('label'));
        autocompleteList.hide();

        field.on("keyup paste", function() {
            value = field.val();
            if(value == lastValue) {
                return;
            }
            data = {};
            data[settings.queryParamName] = value;
            if(settings.extraFields) {
                var form = field.closest('form');
                $.each(settings.extraFields.split(':'), function(i, name) {
                    data[name] = $('[name=' + name + ']', form).val();
                });
            }
            $.get(settings.url, data, function(responseData) {
                updateAutocomplete(responseData);
            });
            lastValue = value;
        }).on("focusout", function(evt) {
            autocompleteList.hide();
        }).on("focusin", function() {
            if($('li', autocompleteList).length > 0) {
                autocompleteList.show();
            }
        });

        function updateAutocomplete(responseData) {
            if(responseData.length == 0) {
                autocompleteList.hide();
                return;
            }
            autocompleteList.show();
            $('li', autocompleteList).remove();
            $.each(responseData, function(i, item) {
                var link = $('<a href="#">');
                link.text(item.label);
                link.mousedown(function() {
                    field.val(item.value);
                    autocompleteList.hide();
                });
                autocompleteList.append($('<li>').append(link));
            });
        }
    });
}

$document.ready(function() {
    $('.autocomplete-textbox').autocompleteTextbox();
});

})();
