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

    var root, SubtitleListController, SubtitleListItemController;

    root = this;

    SubtitleListController = function($scope, SubtitleFetcher) {
        $scope.getSubtitles = function(languageCode, versionNumber){
            $scope.items = SubtitleFetcher.getSubtitles(languageCode, versionNumber, function(subtitlesXML){
                $scope.onSubtitlesFetched(subtitlesXML);
            });
        }
        $scope.onSubtitlesFetched = function (dfxpXML){

            this.dfxpWrapper = new AmaraDFXPParser();
            this.dfxpWrapper.init(dfxpXML);
            // now populate the subtitles scope var
            // and let angular build the UI
            var subtitlesData = _.map(this.dfxpWrapper.getSubtitles(), function(sub,i){
                    return {
                        index: i,
                        startTime: this.dfxpWrapper.startTime(i),
                        endTime: this.dfxpWrapper.endTime(i),
                        text: this.dfxpWrapper.content(i)

                    }
                }, this);
            $scope.subtitlesData = subtitlesData;
            $scope.$broadcast("onSubtitlesFetched");


        }
    };

    SubtitleListItemController  = function($scope, SubtitleFetcher){
        // we expect to have on the scope:
        // listController : SubtitleListController
        // index: my index
        $scope.toHTML = function  (markupLikeText) {

        }
        $scope.startEditingMode = function (){

        }
        $scope.finishEditingMode = function(){

        }
    }
    // exports
    root.SubtitleListController = SubtitleListController;
    root.SubtitleListItemController = SubtitleListItemController;



}).call(this);