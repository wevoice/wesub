(function ($) {

    var directives = angular.module("amara.SubtitleEditor.directives", []);
    directives.directive("subtitleList", function (SubtitleFetcher) {
        var isEditable;
        var selectedScope, selectedController;

        /**
         * Triggered with a key is up on a text area for editing subtitles.
         * If it's regular text just do the default thing.
         * If we pressed an enter / return, finish editing this sub and
         * focus o the next one. Same for tab
         * @param e The jQuery key event
         */
        function onSubtitleTextKeyUp(e) {

            var keyCode = e.keyCode;


            if (event.keyCode == 13 && !event.shiftKey) {
                // enter with shift means new line
                selectedScope.textChanged($(e.currentTarget).text());
                e.preventDefault();
                selectedScope.$digest();
            }
        }

        /**
         * Receives the li.subtitle-list-item to be edited.
         * Will put any previously edited ones in display mode,
         * mark this one as being edited, creating the textarea for
         * editing.
         */
        function onSubtitleItemSelected(elm) {
            var controller = angular.element(elm).controller();
            var scope = angular.element(elm).scope();
            // make sure the user clicked on the list item
            if (controller instanceof SubtitleListItemController) {
                var textarea = $("textarea", $(elm).parent(".subtitle-list-item"));
                if (selectedScope) {
                    // if there were an active item, deactivate it
                    selectedScope.finishEditingMode(textarea.text());
                    // trigger updates
                    selectedScope.$digest();
                }
                selectedScope = scope;
                var editableText = selectedScope.startEditingMode();

                textarea.text(editableText);
                selectedScope.$digest();
            }
        }

        return {

            compile:function compile(elm, attrs, transclude) {
                // should be on post link so to give a chance for the
                // nested directive (subtitleListItem) to run
                return {
                    post:function post(scope, elm, attrs) {
                        scope.getSubtitles(attrs.languageCode, attrs.versionNumber);

                        isEditable = attrs.editable === 'true';
                        // if is editable, hook up event listeners
                        if (isEditable) {
                            $(elm).click(function (e) {
                                onSubtitleItemSelected(e.srcElement);
                            });
                            $(elm).on("keyup", "textarea", onSubtitleTextKeyUp);
                        }
                    }
                };
            }
        };
    });
    directives.directive("subtitleListItem", function (SubtitleFetcher) {
        return {
            link:function link(scope, elm, attrs) {

            }
        };

    });

})(window.AmarajQuery);
