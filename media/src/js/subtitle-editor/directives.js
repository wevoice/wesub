var directives = angular.module("amara.SubtitleEditor.directives", []);
directives.directive("subtitleList", function(SubtitleFetcher){
    return {
        link: function link(scope, elm, attrs){
            scope.getSubtitles(attrs.languageCode, attrs.versionNumber);

        }
    }

});