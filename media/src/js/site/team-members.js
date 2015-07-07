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

})();
