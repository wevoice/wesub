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

(function() {

    var root = this;
    var _ = root._.noConflict();
    var $ = root.AmarajQuery;

    var LanguageSelectorController = function($scope, SubtitleStorage, SubtitleListFinder) {
        /**
         * This controller is responsible for the language and version selector
         * widget.  The widget allows the user to select a reference language and
         * version when translating subtitles into another language.
         *
         * The $scope contains 'languages' and 'versions'.  Each list is
         * represented in the UI as a <select> element.  The selected language or
         * version is stored on the $scope as a 'language' and 'version' model.
         *
         * Whenever the language selection is changed, we update the list of
         * versions.  When a new version is selected, we retrieve the subtitles
         * (either from memory or from the API via ajax) and display them in the
         * side panel.
         */

        $scope.languageSelectChanged = function(lang) {
            var vers, language;

            if (lang) {
                language = lang;
            } else {
                language = $scope.language;
            }

            if (!language) {
                return;
            }

            vers =_.sortBy(language.versions, function(item) {
                return item.version_no;
            });

            $scope.versions = vers.reverse();

            if (vers.length && vers.length > 0) {
                $scope.version = $scope.versions[0];
            }
        };
        $scope.setReferenceSubs = function(subtitlesXML) {
            if (!$scope.refSubList) {
                $scope.refSubList = SubtitleListFinder.get('reference-subtitle-set');
            }
            $scope.refSubList.scope.onSubtitlesFetched(subtitlesXML);
        };
        $scope.versionChanged = function(newVersion) {
            var subtitlesXML;

            if (!newVersion) {
                return;
            }
            subtitlesXML = newVersion.subtitlesXML;

            if (!subtitlesXML) {
                SubtitleStorage.getSubtitles($scope.language.code,
                                             newVersion.version_no,
                                             function(subtitlesXML) {
                    $scope.version.subtitlesXML = subtitlesXML;
                    $scope.setReferenceSubs(subtitlesXML);
                });
            } else {
                $scope.setReferenceSubs(subtitlesXML);
            }
        };

        SubtitleStorage.getLanguages(function(languages) {
            $scope.languages = languages;
            $scope.language = _.find(languages, function(item) {
                return item.editingLanguage;
            });
            $scope.languageSelectChanged($scope.language);
        });

        $scope.$watch('version', $scope.versionChanged);
    };
    var SaveSessionController = function($scope, SubtitleListFinder, SubtitleStorage) {

        $scope.cancel = function($event) {

            $event.preventDefault();

            var subtitleListScope = SubtitleListFinder.get('working-subtitle-set').scope;

            $scope.$root.$emit('show-loading-modal', 'Canceled. Redirecting…');
            window.location = '/videos/' + subtitleListScope.videoID;

        };
        $scope.getNotes = function() {
            var collabScope = angular.element($('section.collab').get(0)).scope();
            return collabScope.notes || '';
        };
        $scope.saveAndApprove = function($event) {

            $scope.saveSession().then(function(response) {
                if ($scope.status === 'saved') {

                    $scope.status = 'approving';

                    SubtitleStorage.approveTask(response, $scope.getNotes()).then(function onSuccess(response) {

                        $scope.$root.$emit('show-loading-modal', 'Subtitles saved, task approved. Redirecting…');
                        window.location = response['data']['site_url'];

                    }, function onError() {
                        $scope.status = 'error';
                        window.alert('Sorry, there was an error...');
                    });
                }
            });

        };
        $scope.saveAndExit = function($event) {

            $event.preventDefault();

            $scope.saveSession().then(function(response) {
                if ($scope.status === 'saved') {

                    $scope.$root.$emit('show-loading-modal', 'Subtitles saved! Redirecting…');
                    window.location = response['data']['site_url'];

                }
            });
        };
        $scope.saveAndSendBack = function() {
            $scope.saveSession().then(function(response) {
                if ($scope.status === 'saved') {

                    $scope.status = 'sending-back';

                    SubtitleStorage.sendBackTask(response, $scope.getNotes()).then(function onSuccess(response) {

                        $scope.$root.$emit('show-loading-modal', 'Subtitles saved, task sent back. Redirecting…');
                        window.location = response['data']['site_url'];
                        
                    }, function onError() {
                        $scope.status = 'error';
                        window.alert('Sorry, there was an error...');
                    });

                }
            });
        };
        $scope.saveSession = function() {
            if ($scope.status !== 'saving') {
                $scope.status = 'saving';

                var promise = SubtitleListFinder.get('working-subtitle-set').scope.saveSubtitles();

                promise.then(function onSuccess(response) {
                    $scope.status = 'saved';
                }, function onError() {
                    $scope.status = 'error';
                    window.alert('Sorry, there was an error...');
                });

                return promise;
            }
        };
        $scope.toggleSaveDropdown = function($event) {
            $scope.dropdownOpen = !$scope.dropdownOpen;
            $event.preventDefault();
        };

        $scope.$root.$on('approve-task', function() {
            $scope.saveAndApprove();
        });
        $scope.$root.$on('send-back-task', function() {
            $scope.saveAndSendBack();
        });
        $scope.$root.$on('work-done', function() {
            $scope.canSave = '';
            $scope.$digest();
        });

    };
    var SubtitleListController = function($scope, $timeout, SubtitleStorage) {
        /**
         * Responsible for everything that touches subtitles as a group,
         * souch as populating the list with actual data, removing subs,
         * adding subs.
         * @param $scope
         * @param SubtitleStorage
         * @constructor
         */

        $scope.addSubtitle = function(index, attrs, content, focus) {

            // Add the subtitle directly to the DFXP instance.
            var newSubtitle = $scope.parser.addSubtitle(index, attrs, content);

            // If we want to focus the subtitle after it's been added, set
            // the index here.
            if (focus) {
                $scope.focusIndex = $scope.parser.getSubtitleIndex(newSubtitle, $scope.parser.getSubtitles().get());

            // Otherwise, reset the focusIndex.
            } else {
                $scope.focusIndex = null;
            }

            // Update the subtitles on the list scope.
            $scope.updateParserSubtitles();
        };
        $scope.getSubtitleListHeight = function() {
            return $(window).height() - 359;
        };
        $scope.getSubtitles = function(languageCode, versionNumber) {
            // if this version has no default source translation language
            // it will be empty, in which case we want to wait for user
            // interaction to request a reference subtitle set.
            if (!languageCode || !versionNumber) {
                $scope.status = 'idle';
                return;
            }
            $scope.status = 'loading';
            $scope.items = SubtitleStorage.getSubtitles(languageCode, versionNumber, function(subtitlesXML) {
                $scope.onSubtitlesFetched(subtitlesXML);
            });
        };
        $scope.onSubtitlesFetched = function (dfxpXML) {
            /**
             * Once we have the dfxp from the server,
             * massage the data as a simpler object and set it on the
             * template. Angular will pick up the change (from the broadcast)
             * and will re-render the UI.
             * @param dfxpXML
             */

            this.dfxpWrapper = new root.AmaraDFXPParser();
            this.dfxpWrapper.init(dfxpXML);

            $scope.parser = this.dfxpWrapper;
            $scope.subtitles = $scope.parser.getSubtitles().get();

            $scope.status = 'ready';

            // When we have subtitles for an editable set, tell the kids.
            $timeout(function() {
                if ($scope.isEditable) {
                    $scope.$broadcast('subtitlesFetched');
                }
            });
        };
        $scope.removeSubtitle = function(subtitle) {
            $scope.parser.removeSubtitle(subtitle);
            $scope.updateParserSubtitles();
        };
        $scope.saveSubtitles = function() {
            $scope.status = 'saving';
            return SubtitleStorage.saveSubtitles($scope.videoID,
                                          $scope.languageCode,
                                          $scope.parser.xmlToString(true, true));
        };
        $scope.setLanguageCode = function(languageCode) {
            $scope.languageCode = languageCode;
        };
        $scope.setVideoID = function(videoID) {
            $scope.videoID = videoID;
        };
        $scope.updateParserSubtitles = function() {
            $scope.subtitles = $scope.parser.getSubtitles().get();
        };

        $scope.$watch($scope.getSubtitleListHeight, function(newHeight) {
            $($('div.subtitles').height(newHeight));
        });

        window.onresize = function() {
            $scope.$digest();
        };
    };
    var SubtitleListHelperController = function($scope) {

        $scope.isEditingAny = false;

        $scope.$root.$on('editing', function() {
            $scope.isEditingAny = true;
            $scope.$digest();
        });
        $scope.$root.$on('editingDone', function() {
            $scope.isEditingAny = false;
            $scope.$digest();
        });
    };
    var SubtitleListItemController = function($scope) {
        /**
         * Responsible for actions on one subtitle: editing, selecting.
         * @param $scope
         * @constructor
         */

        var initialText;

        $scope.empty = false;
        $scope.isEditing = false;
        $scope.showStartTime = $scope.parser.startTimeFromNode($scope.subtitle) > 0;

        $scope.finishEditingMode = function(newValue) {

            $scope.isEditing = false;

            // Tell the root scope that we're no longer editing, now.
            $scope.$root.$emit('editingDone');

            var content = $scope.parser.content($scope.subtitle, newValue);

            if (content !== initialText) {
                $scope.$root.$emit('work-done');
            }
        };
        $scope.getSubtitleIndex = function() {
            return $scope.parser.getSubtitleIndex($scope.subtitle, $scope.subtitles);
        };
        $scope.startEditingMode = function() {

            initialText = $scope.parser.content($scope.subtitle);

            $scope.isEditing = true;

            // Tell the root scope that we're editing, now.
            $scope.$root.$emit('editing');

            return initialText;
        };

        $scope.$on('subtitlesFetched', function() {
            // When subtitles are first retrieved, we need to set up the amarasubtitle
            // on the video and bind to this scope.
            //
            // This will happen on the video controller. Just throw an event stating that
            // we're ready.

            $scope.$root.$emit('subtitleReady', $scope);
        });
    };
    var VideoTitleController = function($scope, SubtitleStorage) {
        $scope.title = "Oh hai.";
    };

    root.LanguageSelectorController = LanguageSelectorController;
    root.SaveSessionController = SaveSessionController;
    root.SubtitleListController = SubtitleListController;
    root.SubtitleListHelperController = SubtitleListHelperController;
    root.SubtitleListItemController = SubtitleListItemController;
    root.VideoTitleController = VideoTitleController;

}).call(this);
