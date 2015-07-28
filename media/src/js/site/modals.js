/* Amara, universalsubtitles.org
 *
 * Copyright (C) 2013 Participatory Culture Foundation
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

$.fn.openModal = function() {
    this.each(function() {
        var modal = $(this);
        var closeButton = $('button.close', modal);

        modal.addClass('shown');
        $('body').append('<div class="modal-overlay"></div>');
        closeButton.bind('click.modal', onClose);
        $document.bind('click.modal', function(evt) {
            var clickedModal = $(evt.target).closest('aside.modal');
            if(clickedModal.length == 0) {
                // click outside the modal
                onClose(evt);
            } else if($(evt.target).closest('button.close', clickedModal).length > 0) {
                // click on the close button
                onClose(evt);
            }
        });
        $document.bind('keydown.modal', function(evt) {
            if (evt.keyCode === 27) {
                onClose(evt);
            }
        });

        function onClose(evt) {
            evt.preventDefault();
            evt.stopPropagation();
            modal.removeClass('shown');
            $('body div.modal-overlay').remove();
            closeButton.unbind('click.modal');
            $document.unbind('click.modal');
            $document.unbind('keydown.modal');
        }
    });
}

$document.ready(function() {
    $('.open-modal').each(function() {
        var link = $(this);
        var modal = $('#' + link.data('modal'));

        link.bind('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            modal.openModal();
            if(link.data('clear-errors')) {
                $('ul.errorlist', modal).remove();
            }
            if(link.data('heading')) {
                $('h3', modal).text(link.data('heading'));
            }
            if(link.data('text')) {
                $('.text', modal).text(link.data('text'));
            }
            if(link.data('setFormValues')) {
                $.each(link.data('setFormValues'), function(name, value) {
                    $('*[name=' + name + ']', modal).val(value);
                });
            }
        });
    });

    $('aside.modal.start-open').openModal();
});

})();
