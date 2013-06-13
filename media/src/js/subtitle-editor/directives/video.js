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
    var directives = angular.module('amara.SubtitleEditor.directives.video', []);

    directives.directive('volumeBar', function(VideoPlayer) {
        return function link($scope, elem, attrs) {
            elem = $(elem);
            var canvas = elem[0];
            var width = 40;
            var barHeight = 95;
            var topHeight = 9;
            var bottomHeight = 9;
            var paddingTop = 10;
            var paddingBottom = 5;
            var slices = $('div', elem);

            function drawBar() {
                var drawHeight = Math.round($scope.videoState.volume *
                    barHeight);
                if(drawHeight <= bottomHeight) {
                    slices.eq(0).height(0);
                    slices.eq(1).height(0);
                    slices.eq(2).height(drawHeight);
                    slices.eq(2).css('background-position',
                        'center ' + drawHeight + 'px');
                } else if(drawHeight <= barHeight - bottomHeight) {
                    slices.eq(0).height(0);
                    slices.eq(1).height(drawHeight - bottomHeight);
                    slices.eq(2).height(bottomHeight);
                    slices.eq(2).css('background-position', 'center 0');
                } else {
                    slices.eq(0).height(drawHeight -
                            (barHeight - bottomHeight));
                    slices.eq(1).height(barHeight - bottomHeight - topHeight);
                    slices.eq(2).height(bottomHeight);
                    slices.eq(2).css('background-position', 'center 0');
                }
                slices.eq(0).css('margin-top',
                        (barHeight - drawHeight) + 'px');
            }

            $scope.$watch('videoState.volume', drawBar);

            function setVolumeFromPageY(pageY) {
                var barBottom = elem.offset().top + barHeight + paddingTop;
                var volume = (barBottom - pageY) / barHeight;
                volume = Math.max(0.0, Math.min(1, volume));
                VideoPlayer.setVolume(volume);
            }

            $scope.onVolumeMouseDown = function(event) {
                setVolumeFromPageY(event.pageY);
                $(document).on('mousemove.volume-track', function(event) {
                    setVolumeFromPageY(event.pageY);
                }).on('mouseup.volume-track', function(event) {
                    $(document).off('.volume-track');
                }).on('mouseleave.volume-track', function(event) {
                    $(document).off('.volume-track');
                });
                event.preventDefault();
            };

            drawBar();
        }
    });
    directives.directive('progressBar', function(VideoPlayer) {
        return function link($scope, elem, attrs) {
            elem = $(elem);
            var sliceLeft = $('div.slice-left div', elem);
            var sliceRight = $('div.slice-right div', elem);
            var sliceMid = $('div.slice-mid div', elem);
            var leftWidth = 14;
            var rightWidth = 14;

            function drawBar() {
                if($scope.videoState.currentTime === null ||
                    $scope.videoState.duration === null) {
                    return;
                }
                var progress = ($scope.videoState.currentTime /
                    $scope.videoState.duration);
                var barWidth = Math.round(elem.width())
                var drawWidth = Math.round(barWidth * progress);
                if(drawWidth <= leftWidth) {
                    sliceLeft.width(drawWidth);
                    sliceMid.width(0);
                    sliceRight.width(0);
                } else if(drawWidth <= barWidth - leftWidth) {
                    sliceLeft.width(leftWidth);
                    sliceMid.width(drawWidth - leftWidth);
                    sliceRight.width(0);
                } else {
                    sliceLeft.width(leftWidth);
                    sliceMid.width(barWidth - leftWidth - rightWidth);
                    sliceRight.width(drawWidth - (barWidth - leftWidth));
                }
            }

            drawBar();
            $scope.$watch('videoState.currentTime', drawBar);
            $scope.$watch('videoState.duration', drawBar);

            function setProgressFromPageX(pageX) {
                if($scope.videoState.duration === null) {
                    return;
                }
                var deltaX = pageX - elem.offset().left;
                var progress = deltaX / elem.width();
                progress = Math.max(0, Math.min(1, progress));

                VideoPlayer.seek(progress * $scope.videoState.duration);
            }

            $scope.onProgressMouseDown = function(event) {
                setProgressFromPageX(event.pageX);
                $(document).on('mousemove.progress-track', function(event) {
                    setProgressFromPageX(event.pageX);
                }).on('mouseup.progress-track', function(event) {
                    $(document).off('.progress-track');
                }).on('mouseleave.progress-track', function(event) {
                    $(document).off('.progress-track');
                });
                event.preventDefault();
            };
        }

    });
})(window.AmarajQuery);

