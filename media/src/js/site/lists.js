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

$(document).ready(function() {
    $('ul.thumb-list.bulk-mode').each(handleThumbListSelection);
});

function handleThumbListSelection() {
    var thumbnails = $('ul.thumb-list .thumb');
    var checkboxes = $('.selection', thumbnails);
    var selectAll = $('.select-all-thumbs input').eq(0);
    var deselectAll = $('button.deselect-all');
    updateSelectionSenstiveElts();
    thumbnails.click(onThumbClicked);
    selectAll.change(onSelectAllChange);
    deselectAll.click(onDeselectAll);

    function onThumbClicked(evt) {
        var checkbox = $('input.selection', this);
        if(checkbox.length > 0) {
            checkbox.prop('checked', !checkbox.prop('checked'));
            evt.preventDefault();
            evt.stopPropagation();
            updateSelectionSenstiveElts();
        }
    }

    function onSelectAllChange(evt) {
        checkboxes.prop('checked', selectAll.prop('checked'));
        updateSelectionSenstiveElts();
    }

    function onDeselectAll(evt) {
        checkboxes.prop('checked', false);
        updateSelectionSenstiveElts();
    }

    function setComponentsEnabled(selector, enabled) {
        if(enabled) {
            selector.removeClass('hidden');
        } else {
            selector.addClass('hidden');
        }
        $('input', selector).prop('disabled', !enabled);
    }

    function updateSelectionSenstiveElts() {
        var checkCount = checkboxes.filter(':checked').length;
        setComponentsEnabled($('.needs-one-selected'), checkCount > 0);
        setComponentsEnabled($('.needs-multiple-selected'), checkCount > 1);
        setComponentsEnabled($('.needs-all-selected'),
                checkCount == checkboxes.length);
        selectAll.prop('checked', checkCount == checkboxes.length);
        updateButtomSheet(checkCount);
    }

    function updateButtomSheet(checkCount) {
        if(checkCount > 0) {
            bottomSheet.show();
            // FIXME: This code should use ngettext, but we don't have it set
            // up in javascript
            if(checkCount == 1) {
                var title = $('.bottom-sheet').data('titleSingular');
            } else {
                var title = $('.bottom-sheet').data('titlePlural')
                    .replace('COUNT_PLACEHOLDER', checkCount);
            }
            bottomSheet.setHeading(title);
        } else {
            bottomSheet.hide();
        }
    }
}

})();
