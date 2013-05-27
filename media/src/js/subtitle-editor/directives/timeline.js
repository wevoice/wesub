// Amara, universalsubtitles.org
//
// Copyright (C) 2013 Participatory Culture Foundation
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see
// http://www.gnu.org/licenses/agpl-3.0.html.

var angular = angular || null;

(function($) {
    var MIN_DURATION = 250; // 0.25 seconds

    var directives = angular.module('amara.SubtitleEditor.directives.timeline', []);

    function calcTimelineView(scope, width) {
        // Calculate the portion of the video time that is displayed in the
        // timeline

        var widthPerSecond = Math.floor(scope.scale * 100);
        // put startTime in the middle of the canvas
        var timelineDuration = width * 1000 / widthPerSecond;
        var startTime = scope.currentTime - timelineDuration / 2;
        return {
            'startTime': startTime,
            'widthPerSecond': widthPerSecond,
            'endTime': startTime + timelineDuration,
        }
    }

    directives.directive('timelineTiming', function() {
        var width=0, height=65; // dimensions of the canvas
        var view = null;

        function resizeCanvas(elem) {
            // Resize the canvas so that it's width matches the
            // width of its container, but also make sure that it's a whole
            // number of pixels.
            var canvas = elem[0];
            width = canvas.width = Math.floor($(elem).parent().width());
            $(elem).css('width', width + 'px');
        }
        function trackWindowResize(scope, elem) {
            $(window).resize(function() {
                resizeCanvas(elem);
                drawCanvas(scope, elem);
            });
        }
        function drawSecond(ctx, xPos, t) {
            // draw the second text on the timeline
            ctx.fillStyle = '#686868';
            var metrics = ctx.measureText(t);
            var x = xPos - (metrics.width / 2);
            ctx.fillText(t, x, 60);
        }
        function drawTics(ctx, xPos) {
            // draw the tic marks between seconds
            ctx.strokeStyle = '#686868';
            var divisions = 4;
            var step = view.widthPerSecond / divisions;
            ctx.lineWidth = 1;
            ctx.beginPath();
            for(var i = 1; i < divisions; i++) {
                var x = Math.floor(0.5 + xPos + step * i);
                x += 0.5;
                ctx.moveTo(x, 60);
                if(i == divisions / 2) {
                    // draw an extra long tic for the 50% mark;
                    ctx.lineTo(x, 45);
                } else {
                    ctx.lineTo(x, 50);
                }
            }
            ctx.stroke();
        }
        function drawCanvas(scope, elem) {
            var ctx = elem[0].getContext("2d");
            ctx.clearRect(0, 0, width, height);
            ctx.font = 'bold ' + (height / 5) + 'px sans';

            view = calcTimelineView(scope, width);
            var startTime = Math.floor(Math.max(view.startTime / 1000, 0));
            if(scope.duration !== null) {
                var endTime = Math.floor(Math.min(view.endTime / 1000,
                            scope.duration / 1000));
            } else {
                var endTime = Math.floor(view.endTime / 1000);
            }

            for(var t = startTime; t < endTime; t++) {
                var xPos = (t - (view.startTime / 1000)) * view.widthPerSecond;
                drawSecond(ctx, xPos, t);
                drawTics(ctx, xPos);
            }
        }
        return function link(scope, elem, attrs) {
            resizeCanvas(elem);
            trackWindowResize(scope, elem);
            scope.$watch('currentTime + ":" + duration',
                function(newValue, oldValue) {
                    drawCanvas(scope, elem);
            });
        }
    });
    directives.directive('timelineSubtitles', function() {
        return function link(scope, elem, attrs) {
            var view = null;
            var container = $(elem);
            // Map XML subtitle nodes to the div we created to show them
            var timelineDivs = {}

            function handleDragLeft(context, deltaMSecs) {
                context.startTime = context.subtitle.startTime + deltaMSecs;
                if(context.startTime < context.minStartTime) {
                    context.startTime = context.minStartTime;
                }
                if(context.startTime > context.endTime - MIN_DURATION) {
                    context.startTime = context.endTime - MIN_DURATION;
                }
            }

            function handleDragRight(context, deltaMSecs) {
                context.endTime = context.subtitle.endTime + deltaMSecs;
                if(context.maxEndTime !== null &&
                    context.endTime > context.maxEndTime) {
                    context.endTime = context.maxEndTime;
                }
                if(context.endTime < context.startTime + MIN_DURATION) {
                    context.endTime = context.startTime + MIN_DURATION;
                }
            }

            function handleDragMiddle(context, deltaMSecs) {
                context.startTime = context.subtitle.startTime + deltaMSecs;
                context.endTime = context.subtitle.endTime + deltaMSecs;

                if(context.startTime < context.minStartTime) {
                    context.startTime = context.minStartTime;
                    context.endTime = (context.startTime +
                            context.subtitle.duration());
                }
                if(context.endTime > context.maxEndTime) {
                    context.endTime = context.maxEndTime;
                    context.startTime = (context.endTime -
                            context.subtitle.duration());
                }

            }

            function handleMouseDown(evt, dragHandler) {
                var subtitle = evt.data.subtitle;
                var dragHandler = evt.data.dragHandler;
                var context = {
                    subtitle: subtitle,
                    startTime: subtitle.startTime,
                    endTime: subtitle.endTime,
                }
                var subtitleList = scope.workingSubtitles.subtitleList;
                var nextSubtitle = subtitleList.nextSubtitle(subtitle);
                if(nextSubtitle && nextSubtitle.isSynced()) {
                    context.maxEndTime = nextSubtitle.startTime;
                } else {
                    context.maxEndTime = scope.duration;
                }
                var prevSubtitle = subtitleList.prevSubtitle(subtitle);
                if(prevSubtitle) {
                    context.minStartTime = prevSubtitle.endTime;
                } else {
                    context.minStartTime = 0;
                }

                var div = timelineDivs[context.subtitle.id];
                if(div === undefined) {
                    return;
                }
                var initialPageX = evt.pageX;
                container.on('mousemove.timelinedrag', function(evt) {
                    var deltaX = evt.pageX - initialPageX;
                    var deltaMSecs = deltaX * 1000 / view.widthPerSecond;
                    dragHandler(context, deltaMSecs);
                    placeSubtitle(context.startTime, context.endTime, div);
                }).on('mouseup.timelinedrag', function(evt) {
                    container.off('.timelinedrag');
                    var subtitleList = scope.workingSubtitles.subtitleList;
                    subtitleList.updateSubtitleTime(context.subtitle,
                        context.startTime, context.endTime);
                    scope.$root.$digest();
                }).on('mouseleave.timelinedrag', function(evt) {
                    container.off('.timelinedrag');
                    placeSubtitle(subtitle.startTime, subtitle.endTime, div);
                });
                // need to prevent the default event from happening so that the
                // browser's DnD code doesn't mess with us.
                evt.preventDefault();
                return false;
            }

            function makeDivForSubtitle(subtitle) {
                var div = $('<div/>', {class: 'subtitle'});
                var span = $('<span/>');
                span.html(subtitle.content());
                var left = $('<a href="#" class="handle left"></a>');
                var right = $('<a href="#" class="handle right"></a>');
                left.on('mousedown',
                        {subtitle: subtitle, dragHandler: handleDragLeft},
                        handleMouseDown);
                right.on('mousedown',
                        {subtitle: subtitle, dragHandler: handleDragRight},
                        handleMouseDown);
                span.on('mousedown',
                        {subtitle: subtitle, dragHandler: handleDragMiddle},
                        handleMouseDown);
                div.append(left);
                div.append(span);
                div.append(right);
                container.append(div);
                return div;
            }

            function placeSubtitle(startTime, endTime, div) {
                var x = Math.floor((startTime - view.startTime) *
                    view.widthPerSecond / 1000);
                var width = Math.floor((endTime - startTime) *
                    view.widthPerSecond / 1000);
                div.css({left: x, width: width});
            }

            function placeSubtitles() {
                if(!scope.workingSubtitles) {
                    return;
                }
                var subtitles = scope.workingSubtitles.subtitleList.getSubtitlesForTime(
                    view.startTime, view.endTime);


                var oldTimelineDivs = timelineDivs;
                timelineDivs = {}

                for(var i = 0; i < subtitles.length; i++) {
                    var subtitle = subtitles[i];
                    if(oldTimelineDivs.hasOwnProperty(subtitle.id)) {
                        timelineDivs[subtitle.id] = oldTimelineDivs[subtitle.id];
                        delete oldTimelineDivs[subtitle.id];
                    } else {
                        var div = makeDivForSubtitle(subtitle);
                        timelineDivs[subtitle.id] = div;
                    }
                    placeSubtitle(subtitle.startTime, subtitle.endTime,
                            timelineDivs[subtitle.id]);
                }
                // remove divs no longer in the timeline
                for(var subId in oldTimelineDivs) {
                    oldTimelineDivs[subId].remove();
                }
            }
            scope.$watch('currentTime + ":" + duration',
                function(newValue, oldValue) {
                    view = calcTimelineView(scope, container.width());
                    placeSubtitles();
            });
            scope.$root.$on('work-done', function() {
                placeSubtitles();
            });
            scope.$root.$on('subtitles-fetched', function() {
                placeSubtitles();
            });
        }
    });

})(window.AmarajQuery);
