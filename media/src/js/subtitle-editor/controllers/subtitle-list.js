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

    var root, SubtitleListController, SubtitleListItemController,
        HelperSelectorController;

    root = this;

    /**
     * Responsible for everything that touches subtitles as a group,
     * souch as populating the list with actual data, removing subs,
     * adding subs.
     * @param $scope
     * @param SubtitleStorage
     * @constructor
     */
    SubtitleListController = function($scope, SubtitleStorage) {
        $scope.getSubtitles = function(languageCode, versionNumber) {
            $scope.status = 'loading';
            $scope.items = SubtitleStorage.getSubtitles(languageCode, versionNumber, function(subtitlesXML) {
                $scope.onSubtitlesFetched(subtitlesXML);
            });
        };
        /**
         * Once we have the dfxp from the server,
         * massage the data as a simpler object and set it on the
         * template. Angular will pick up the change (from the broadcast)
         * and will re-render the UI.
         * @param dfxpXML
         */
        $scope.onSubtitlesFetched = function (dfxpXML) {

            this.dfxpWrapper = new AmaraDFXPParser();
            this.dfxpWrapper.init(dfxpXML);
            // now populate the subtitles scope var
            // and let angular build the UI
            var subtitles = this.dfxpWrapper.getSubtitles();
            // preallocate array, gives us a small perf gain
            // on ie / safari
            var subtitlesData = new Array(subtitles.length);
            for (var i=0; i < subtitles.length; i++){
                subtitlesData[i] =  {
                    index: i,
                    startTime: this.dfxpWrapper.startTime(subtitles.eq(i).get(0)),
                    endTime: this.dfxpWrapper.endTime(subtitles.eq(i).get(0)),
                    text: this.dfxpWrapper.contentRendered(subtitles.eq(i).get(0))
                };
            }
            $scope.subtitlesData = subtitlesData;
            // only let the descendant scope know of this, no need to propagate
            // upwards
            $scope.status = 'ready';
            $scope.$broadcast("onSubtitlesFetched");

        };
        $scope.setSelectedIndex = function(index){
            $scope.selectedIndex = index;
            $scope.$digest();
        };

        $scope.setVideoID = function(videoID){
            $scope.videoID = videoID;
        };

        $scope.setLanguageCode = function(languageCode){
            $scope.languageCode = languageCode;
        };
        $scope.saveSubtitles = function(){
            SubtitleStorage.saveSubtitles(scope.videoID, scope.languageCode, this.dfxpWrapper.xmlToString(true, true));
            $scope.status = 'saving';
        }
    };

    /**
     * Responsible for actions on one subtitle: editing, selecting.
     * @param $scope
     * @constructor
     */
    SubtitleListItemController = function($scope, SubtitleStorage) {
        // we expect to have on the scope the object that
        // SubtitleListController.onSubtitlesFetched
        // has created from the dfxp

        $scope.isEditing = false;
        $scope.toHTML = function(markupLikeText) {
        };

        $scope.startEditingMode = function() {
            $scope.isEditing  = true;
            // fix me, this should return the markdown text
            return this.dfxpWrapper.content($scope.subtitle.index)
        };
        $scope.finishEditingMode = function(newValue){
            $scope.isEditing  = false;
            this.dfxpWrapper.content($scope.getSubtitleNode(), newValue);
            $scope.subtitle.text = this.dfxpWrapper.contentRendered($scope.getSubtitleNode());
        };

        $scope.getSubtitleNode = function() {
            return this.dfxpWrapper.getSubtitle($scope.subtitle.index);
        };

        $scope.setEditable = function(isEditable) {
        };

        $scope.textChanged = function(newText) {
            $scope.subtitle.text = newText;
        };
    };

    HelperSelectorController = function($scope, SubtitleStorage) {
        $scope.languageValue = ['en', 'fr', 'cs'];
    };

    // exports
    root.SubtitleListController = SubtitleListController;
    root.SubtitleListItemController = SubtitleListItemController;
    root.HelperSelectorController = HelperSelectorController;

}).call(this);
