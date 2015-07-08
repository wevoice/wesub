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
    $('ul.team-members').each(handleMemberList);
    $('form.team-invite').each(handleInviteForm);
});

function handleMemberList(memberList) {
    $('a.edit', memberList).click(openEditForm);
}

function openEditForm(evt) {
    var link = $(this);
    var form = $('#edit-form');

    $('h3', form).text(link.data('heading'));
    $('#member-id-field', form).val(link.data('member-id'));
    $('#id_role', form).val(link.data('member-role'));

    form.openModal();
    evt.preventDefault();
    evt.stopPropagation();
}

function handleInviteForm(form) {
    var usernameField = $('input[name=username]', form);
    usernameField.autocompleteTextbox({
        url: usernameField.data('search-url'),
        callback: function(userData) {
            return [userData.username, userData.display];
        }
    });
}

/*
function handleInviteForm(form) {
    var usernameField = $('input[name=username]', form);
    var url = usernameField.data('search-url');
    var autocompleteList = $('ul.autocomplete', form);
    var lastQuery = null;

    usernameField.on("keyup paste", function() {
        query = usernameField.val();
        if(query == lastQuery) {
            return;
        }
        $.get(url, {query: query}, function(data) {
            updateAutocomplete(data);
        });
        lastQuery = query;
    }).on("focusout", function() {
        // use setTimeout to ensure if the user clicked on the autocomplete
        // list, we don't hide it before the click event.
        setTimeout(autocompleteList.hide, 0);
    }).on("focusin", function() {
        if(autocompleteList.has('li')) {
            autocompleteList.show();
        }
    });

    function updateAutocomplete(data) {
        autocompleteList.show();
        $('li', autocompleteList).remove();
        $.each(data, function(i, userData) {
            var link = $('<a href="#">');
            link.text(userData.display);
            link.click(function() {
                usernameField.val(userData.username);
                autocompleteList.hide();
            });
            autocompleteList.append($('<li>').append(link));
        });
    }
}
*/

})();
