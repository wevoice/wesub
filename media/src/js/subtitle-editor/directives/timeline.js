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
    var DEFAULT_DURATION = 4000; // 4.0 seconds

    var directives = angular.module('amara.SubtitleEditor.directives.timeline', []);

    function calcTimelineView(scope, width, deltaMSecs) {
        // Calculate the portion of the video time that is displayed in the
        // timeline

        var widthPerSecond = Math.floor(scope.scale * 100);
        // put startTime in the middle of the canvas
        var timelineDuration = width * 1000 / widthPerSecond;
        var startTime = scope.currentTime - timelineDuration / 2;
        if(deltaMSecs) {
            startTime += deltaMSecs;
        }
        return {
            'startTime': startTime,
            'widthPerSecond': widthPerSecond,
            'endTime': startTime + timelineDuration,
        }
    }

    directives.directive('timelineTiming', function() {
        return function link(scope, elem, attrs) {
            var width=0, height=65; // dimensions of the canvas
            var view = null;
            var canvas = $(elem);
            var canvasElt = elem[0];
            var container = canvas.parent();

            function resizeCanvas() {
                // Resize the canvas so that it's width matches the
                // width of its container, but also make sure that it's a whole
                // number of pixels.
                width = canvasElt.width = Math.floor(container.width());
                canvas.css('width', width + 'px');
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
            function drawCanvas() {
                var ctx = canvasElt.getContext("2d");
                ctx.clearRect(0, 0, width, height);
                ctx.font = 'bold ' + (height / 5) + 'px Open Sans';

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

            resizeCanvas();
            $(window).resize(function() {
                resizeCanvas();
                scope.redrawCanvas();
            });
            scope.redrawCanvas = function() {
                view = calcTimelineView(scope, width);
                drawCanvas();
            };
            scope.$on('timeline-drag', function(evt, deltaMSecs) {
                scope.redrawCanvas();
            });
        }
    });
    directives.directive('timelineSubtitles', function(VideoPlayer) {
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
                if(!scope.workingSubtitles.allowsSyncing) {
                    evt.preventDefault();
                    return false;
                }
                VideoPlayer.pause();
                var subtitle = evt.data.subtitle;
                var dragHandler = evt.data.dragHandler;
                var context = {
                    subtitle: subtitle,
                    startTime: subtitle.startTime,
                    endTime: subtitle.endTime,
                }
                if(subtitle.realSubtitle === undefined) {
                    var realSubtitle = subtitle;
                } else {
                    var realSubtitle = subtitle.realSubtitle;
                }
                var subtitleList = scope.workingSubtitles.subtitleList;
                var nextSubtitle = subtitleList.nextSubtitle(realSubtitle);
                if(nextSubtitle && nextSubtitle.isSynced()) {
                    context.maxEndTime = nextSubtitle.startTime;
                } else {
                    context.maxEndTime = scope.duration;
                }
                var prevSubtitle = subtitleList.prevSubtitle(realSubtitle);
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
                $(document).on('mousemove.timelinedrag', function(evt) {
                    var deltaX = evt.pageX - initialPageX;
                    var deltaMSecs = deltaX * 1000 / view.widthPerSecond;
                    dragHandler(context, deltaMSecs);
                    placeSubtitle(context.startTime, context.endTime, div);
                }).on('mouseup.timelinedrag', function(evt) {
                    $(document).off('.timelinedrag');
                    var subtitleList = scope.workingSubtitles.subtitleList;
                    subtitleList.updateSubtitleTime(realSubtitle,
                        context.startTime, context.endTime);
                    scope.$root.$emit("work-done");
                    scope.$root.$digest();
                }).on('mouseleave.timelinedrag', function(evt) {
                    $(document).off('.timelinedrag');
                    placeSubtitle(subtitle.startTime, subtitle.endTime, div);
                });
                // need to prevent the default event from happening so that the
                // browser's DnD code doesn't mess with us.
                evt.preventDefault();
                return false;
            }

            function makeDivForSubtitle(subtitle) {
                if(subtitle.realSubtitle === undefined) {
                    var div = $('<div/>', {class: 'subtitle'});
                } else {
                    var div = $('<div/>', {class: 'subtitle unsynced'});
                }
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

            function updateDivForSubtitle(div, subtitle) {
                $('span', div).html(subtitle.content());
                if(subtitle.isSynced()) {
                    div.removeClass('unsynced');
                }
            }

            function handleMouseDownInTimeline(evt) {
                var initialPageX = evt.pageX;
                $(document).on('mousemove.timelinedrag', function(evt) {
                    VideoPlayer.pause();
                    var deltaX = initialPageX - evt.pageX;
                    var deltaMSecs = deltaX * 1000 / view.widthPerSecond;
                    view = calcTimelineView(scope, container.width(),
                        deltaMSecs);
                    placeSubtitles();
                    scope.$emit('timeline-drag', deltaMSecs);
                }).on('mouseup.timelinedrag', function(evt) {
                    $(document).off('.timelinedrag');
                    var deltaX = initialPageX - evt.pageX;
                    var deltaMSecs = deltaX * 1000 / view.widthPerSecond;
                    VideoPlayer.seek(scope.currentTime + deltaMSecs);
                }).on('mouseleave.timelinedrag', function(evt) {
                    $(document).off('.timelinedrag');
                    view = calcTimelineView(scope, container.width());
                    placeSubtitles();
                    scope.$emit('timeline-drag', 0);
                });
                evt.preventDefault();
            }

            function placeSubtitle(startTime, endTime, div) {
                var x = Math.floor((startTime - view.startTime) *
                        view.widthPerSecond / 1000);
                var width = Math.floor((endTime - startTime) *
                        view.widthPerSecond / 1000);
                div.css({left: x, width: width});
            }

            function addUnsyncedSubtitle(subtitleList, subtitles) {
                /* Add the first unsynced subtitle to the list of subtitles on
                 * the timeline.
                 *
                 * If we should display the subtitle, it will be pushed to the
                 * end of subtitles.
                 */
                var lastSynced = subtitleList.lastSyncedSubtitle();
                if(lastSynced !== null &&
                    lastSynced.endTime > scope.currentTime) {
                    // Not past the end of the synced subtitles
                    return;
                }
                var unsynced = subtitleList.firstUnsyncedSubtitle();
                if(unsynced === null) {
                    return;
                }
                if(unsynced.startTime >= 0 && unsynced.startTime >
                        view.endTime) {
                    // unsynced subtitle has its start time set, and it's past
                    // the end of the timeline.
                    return;
                }
                if(unsynced.startTime < 0) {
                    var startTime = scope.currentTime;
                    var endTime = scope.currentTime + DEFAULT_DURATION;
                } else {
                    var startTime = unsynced.startTime;
                    var endTime = Math.max(scope.currentTime,
                            unsynced.startTime + MIN_DURATION);
                }
                // Make a fake subtitle to show on the timeline.
                subtitles.push({
                    realSubtitle: unsynced,
                    id: unsynced.id,
                    startTime: startTime,
                    endTime: endTime,
                    isAt: function(time) {
                        return startTime <= time && time < endTime;
                    },
                    duration: function() { return endTime - startTime; },
                    content: function() { return unsynced.content() },
                    isSynced: function() { return false; }
                });
            }

            function checkShownSubtitle(subtitles) {
                // Check if a new subtitle is displayed
                var shownSubtitle = null;
                for(var i = 0; i < subtitles.length; i++) {
                    if(subtitles[i].isAt(scope.currentTime)) {
                        shownSubtitle = subtitles[i];
                    }
                }
                if(shownSubtitle != scope.subtitle) {
                    scope.subtitle = shownSubtitle;
                    scope.$root.$emit('timeline-subtitle-shown',
                            shownSubtitle);
                    scope.$root.$digest();
                }
            }

            function placeSubtitles() {
                if(!scope.workingSubtitles) {
                    return;
                }
                var subtitleList = scope.workingSubtitles.subtitleList;
                var subtitles = subtitleList.getSubtitlesForTime(
                        view.startTime, view.endTime);
                var oldTimelineDivs = timelineDivs;
                timelineDivs = {}

                addUnsyncedSubtitle(subtitleList, subtitles);

                for(var i = 0; i < subtitles.length; i++) {
                    var subtitle = subtitles[i];
                    if(oldTimelineDivs.hasOwnProperty(subtitle.id)) {
                        var div = oldTimelineDivs[subtitle.id];
                        timelineDivs[subtitle.id] = div;
                        updateDivForSubtitle(div, subtitle);
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

                checkShownSubtitle(subtitles);
            }
            scope.redrawSubtitles = function() {
                view = calcTimelineView(scope, container.width());
                placeSubtitles();
            };
            scope.$root.$on('work-done', function() {
                scope.redrawSubtitles();
            });
            scope.$root.$on('subtitles-fetched', function() {
                scope.redrawSubtitles();
            });
            container.on('mousedown', handleMouseDownInTimeline);
        }
    });

})(window.AmarajQuery);
