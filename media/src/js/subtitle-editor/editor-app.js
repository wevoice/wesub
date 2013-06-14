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

(function() {

    var root, module;

    root = this;

    module = angular.module('amara.SubtitleEditor', [
        'amara.SubtitleEditor.controllers.app',
        'amara.SubtitleEditor.controllers.collab',
        'amara.SubtitleEditor.controllers.help',
        'amara.SubtitleEditor.controllers.modal',
        'amara.SubtitleEditor.controllers.subtitles',
        'amara.SubtitleEditor.controllers.timeline',
        'amara.SubtitleEditor.controllers.video',
        'amara.SubtitleEditor.services.dom',
        'amara.SubtitleEditor.services.lock',
        'amara.SubtitleEditor.services.subtitles',
        'amara.SubtitleEditor.services.video',
        'amara.SubtitleEditor.directives.subtitles',
        'amara.SubtitleEditor.directives.timeline',
        'amara.SubtitleEditor.directives.video',
        'amara.SubtitleEditor.filters.subtitles',
        'ngCookies'
    ]);

    // instead of using {{ }} for variables, use [[ ]]
    // so as to avoid conflict with django templating
    module.config(function($interpolateProvider) {
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    });

}).call(this);
