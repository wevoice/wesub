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

    var _, root, SubtitleListController, SubtitleListItemController,
        HelperSelectorController, SaveSessionButtonController;

    root = this;
    _ = root._.noConflict();

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
            // if this version has no default source translation language
            // it will be empty, in which case we want to wait for user
            // interaction to request a reference subtitle set.
            if (!languageCode || !versionNumber){
                $scope.status = 'idle';
                return;
            }
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

            this.dfxpWrapper = new root.AmaraDFXPParser();
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
            SubtitleStorage.saveSubtitles($scope.videoID,
                                          $scope.languageCode,
                                          this.dfxpWrapper.xmlToString(true, true));
            $scope.status = 'saving';
        };
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

        var initialText;
        $scope.isEditing = false;
        $scope.toHTML = function(markupLikeText) {
        };

        $scope.startEditingMode = function() {
            initialText =  this.dfxpWrapper.content($scope.subtitle.index);
            $scope.isEditing  = true;
            // fix me, this should return the markdown text
            return initialText;
        };
        $scope.finishEditingMode = function(newValue){
            $scope.isEditing  = false;
            this.dfxpWrapper.content($scope.getSubtitleNode(), newValue);
            $scope.subtitle.text = this.dfxpWrapper.contentRendered($scope.getSubtitleNode());
            if ($scope.subtitle.text != initialText){
                // mark dirty variable on root scope so we can allow
                // saving the session
                $scope.$root.$emit("onWorkDone");
            }
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

    HelperSelectorController = function($scope, SubtitleStorage,
                                        SubtitleListFinder) {

        $scope.getPrimaryAudioLanguage = function(languages) {
            return _.find(languages, function(language) {
                return language.is_primary_audio_language;
            });
        };

        $scope.languageSelectChanged = function(lang) {
            var vers, language;

            if (lang) {
                language = lang;
            } else {
                language = $scope.language;
            }

            vers =_.sortBy(language.versions, function(item) {
                return item.number;
            });
            $scope.versions = vers.reverse();
            if (vers.length && vers.length > 0) {
                $scope.version = $scope.versions[0];
            }
        };

        SubtitleStorage.getLanguages(function(languages) {
            $scope.languages = languages;
            $scope.language = _.find(languages, function(item) {
                return item.editingLanguage;
            });
            $scope.languageSelectChanged($scope.language);
        });

        $scope.versionChanged = function(newVersion, oldVersion) {
            if (!newVersion) {
                return;
            }
            var subtitles = newVersion.subtitlesXML;

            if (!subtitles) {
                throw Error("Version doesn't contain subs.");
            }
            var refSubList = SubtitleListFinder.get('reference-subtitle-set');
            refSubList.scope.onSubtitlesFetched(subtitles);
        };

        $scope.$watch('version', $scope.versionChanged);
    };

    SaveSessionButtonController = function($scope, SubtitleListFinder){
        // since the button can be outside of the subtitle list directive
        // we need the service to find out which set we're saving.
        $scope.saveSession = function(){
            SubtitleListFinder.get('working-subtitle-set').scope.saveSubtitles();
        };
        $scope.$root.$on("onWorkDone", function(){
            $scope.canSave = '';
            $scope.$digest();
        });
    };
    // exports
    root.SubtitleListController = SubtitleListController;
    root.SubtitleListItemController = SubtitleListItemController;
    root.HelperSelectorController = HelperSelectorController;
    root.SaveSessionButtonController = SaveSessionButtonController;

}).call(this);
