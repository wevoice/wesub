(function($) {

    var directives = angular.module("amara.SubtitleEditor.directives", []);

    directives.directive("subtitleList", function(SubtitleFetcher){
        var isEditable, selectedScope, selectedController;
        function onItemClicked(e){
            var controller = angular.element(e.srcElement).controller();
            var scope = angular.element(e.srcElement).scope();
            // make sure the user clicked on the list item
            if (controller instanceof SubtitleListItemController){
                if (selectedScope){
                    selectedScope.finishEditingMode();
                }
                selectedScope = scope;
                selectedScope.startEditingMode();

            }
        }
        return {

            link: function link(scope, elm, attrs){
                scope.getSubtitles(attrs.languageCode, attrs.versionNumber);

                isEditable = attrs.editable === 'true';
                // if is editable, hook up event listeners
                if (isEditable){
                    $(elm).click(onItemClicked);
                }
            }
        };

    });

    directives.directive("subtitleListItem", function(SubtitleFetcher){
        return {
            link: function link(scope, elm, attrs){

            }
        };

    });

})(window.AmarajQuery);
