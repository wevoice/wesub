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

var activeMenu = null;
var toggleAllActive = false;

function openMenu(linkElt) {
    var menuId = linkElt.data('menu');
    $('#' + menuId).show();
    linkElt.addClass('open');
    activeMenu = linkElt;
}
function closeMenu() {
    var menuId = activeMenu.data('menu');
    $('#' + menuId).hide();
    activeMenu.removeClass('open');
    activeMenu = null;
}

$(document).ready(function() {
    $('a.menu-toggle').click(function() {
        var linkElt = $(this);
        if(activeMenu === null) {
            openMenu(linkElt);
        } else if (activeMenu[0] == linkElt[0]) {
            closeMenu();
        } else {
            closeMenu();
            openMenu(linkElt);
        }
    });

    $('button.menu-toggle-all').click(function() {
        var menus = $('ul', $(this).closest('nav'));
        toggleAllActive = !toggleAllActive;
        if(toggleAllActive) {
            menus.slideDown();
        } else {
            menus.slideUp();
        }
    });
});
}(this));
