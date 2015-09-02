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
var dropdown = null;
var toggleAllActive = false;

function openMenu(linkElt) {
    dropdown = linkElt.siblings('ul.dropdown');
    if(linkElt.is('.caret')) {
        linkElt.html('&#9650;');
    }
    if(dropdown.length == 0) {
        return;
    }
    dropdown.show();
    activeMenu = linkElt;
    positionMenu();
    linkElt.addClass('open');
    $(document).bind('click.dropdown', onClickWithOpenDropDown);
}

function closeMenu() {
    if(activeMenu.is('.caret')) {
        activeMenu.html('&#9660;');
    }
    dropdown.hide();
    activeMenu.removeClass('open');
    activeMenu = null;
    $(document).unbind('click.dropdown');
}

function positionMenu() {
    var parentElt = activeMenu.parent();
    var maxLeft = $(window).width() - dropdown.width() - 10;
    // Position the menu at the bottom of the parent element
    dropdown.css('top', parentElt.offset().top + parentElt.height());
    // Position the menu at the left of the dropdown button (but make sure
    // it's not past the edge of the window)
    dropdown.css('left', Math.min(activeMenu.offset().left, maxLeft));
}

function onClickWithOpenDropDown(evt) {
    if($(evt.target).closest('ul.dropdown').length == 0) {
        // click outside the dropdown
        closeMenu();
    }
}

function onMenuToggleClick(evt) {
    var linkElt = $(this);
    if(activeMenu === null) {
        openMenu(linkElt);
    } else if (activeMenu[0] == linkElt[0]) {
        closeMenu();
    } else {
        closeMenu();
        openMenu(linkElt);
    }
    evt.preventDefault();
    evt.stopPropagation();
}

$(document).ready(function() {
    $('a.menu-toggle').click(onMenuToggleClick);
    $('.split-button').each(function() {
        var button = $('button, a.button', this).not('.dropdown button');
        var caret = $('<button>&#9660;</button>')
            .attr('class', button.attr('class'))
            .addClass('caret');
        button.after(caret);
        $('button.caret', this).click(onMenuToggleClick);
    });
    $('.dropdown-button button').click(onMenuToggleClick);

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

$(window).resize(function() {
    if(activeMenu) {
        positionMenu();
    }
});

}(this));
