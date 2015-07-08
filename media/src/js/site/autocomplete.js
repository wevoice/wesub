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
    var settings = $.extend({
        // default options
        queryParamName: 'query',
    }, options);

    this.each(function() {
        var field = $(this);
        var autocompleteList = $('<ul class="autocomplete">');
        var lastValue = null;

        autocompleteList.insertAfter(field.closest('label'));

        field.on("keyup paste", function() {
            value = field.val();
            if(value == lastValue) {
                return;
            }
            data = {};
            data[settings.queryParamName] = value;
            $.get(settings.url, data, function(responseData) {
                updateAutocomplete(responseData);
            });
            lastValue = value;
        }).on("focusout", function() {
            // use setTimeout to ensure if the user clicked on the
            // autocomplete list, we don't hide it before the click event.
            setTimeout(autocompleteList.hide, 0);
        }).on("focusin", function() {
            if(autocompleteList.has('li')) {
                autocompleteList.show();
            }
        });

        function updateAutocomplete(responseData) {
            autocompleteList.show();
            $('li', autocompleteList).remove();
            $.each(responseData, function(i, item) {
                var autocompleteData = settings.callback(item);
                var link = $('<a href="#">');
                link.text(autocompleteData[1]);
                link.click(function() {
                    field.val(autocompleteData[0]);
                    autocompleteList.hide();
                });
                autocompleteList.append($('<li>').append(link));
            });
        }
    });
}

})();
