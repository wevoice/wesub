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

$.fn.withTooltip = function(config) {
    if(config === undefined) {
        config = {};
    }
    this.each(function() {
        var container = $(this);
        var active = false;
        var shown = false;
        var lastMouseMove = null;
        var tooltipDelay = 500;
        var lastX, lastY;

        container.hover(function(evt) {
            active = true;
            lastMouseMove = null;
            container.on('mousemove.tooltip', onMouseMove);
            scheduleTimeout();
            lastX = evt.pageX;
            lastY = evt.pageY;
        }, function(evt) {
            active = false;
            container.off('mousemove.tooltip');
            hideTooltip();
        });

        function getTooltip() {
            if(config.getTooltip) {
                return config.getTooltip(container);
            } else {
                return $('.tooltip', container);
            }
        }

        function scheduleTimeout() {
            if(lastMouseMove === null) {
                var delay = tooltipDelay;
            } else {
                var delay = tooltipDelay - ($.now() - lastMouseMove);
            }
            setTimeout(function() {onTimeout();}, delay);
        }

        function onMouseMove(evt) {
            if(shown) {
                hideTooltip();
                scheduleTimeout();
            }
            lastMouseMove = $.now();
            lastX = evt.pageX;
            lastY = evt.pageY;
        }

        function onTimeout() {
            if(!active) {
                return;
            }
            if(lastMouseMove === null) {
                // no movement, we can show the tooltip
                showTooltip();
            } else {
                // movement, schedule a new timeout
                scheduleTimeout();
                lastMouseMove = null;
            }
        }

        function showTooltip() {
            var tooltip = getTooltip();
            var viewport_bottom = $(window).scrollTop() + $(window).height();
            if(lastY + 10 + tooltip.height() < viewport_bottom) {
                tooltip.css({
                    'left': lastX + 10,
                    'top': lastY + 10
                });
            } else {
                tooltip.css({
                    'left': lastX + 10,
                    'top': viewport_bottom - 10 - tooltip.height()
                });
            }
            tooltip.show();
            shown = true;
        }

        function hideTooltip() {
            getTooltip().hide();
            shown = false;
        }
    });
}

$(document).ready(function() {
    $('.with-tooltip').withTooltip();
});

})();
