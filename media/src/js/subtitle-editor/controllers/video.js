// Amara, universalsubtitles.org
//
// Copyright (C) 2012 Participatory Culture Foundation
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

(function() {

    var root, VideoController;

    root = this;

    /**
     * Responsible for initializing the video.
     * @param $scope
     * @param SubtitleStorage
     * @constructor
     */
    VideoController = function($scope, SubtitleStorage) {
        $scope.pop = Popcorn.smart('#video', SubtitleStorage.getVideoURL());
    };

    // exports
    root.VideoController = VideoController;
    root.SubtitleListItemController = SubtitleListItemController;
    root.HelperSelectorController = HelperSelectorController;

}).call(this);
