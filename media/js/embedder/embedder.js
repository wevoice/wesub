(function(window, document, undefined) {

    // When the embedder is compiled, Underscore.js will be loaded directly before this
    // function. Remap _ to private variable __ and use noConflict() to set _ back to
    // its previous owner.
    var __ = _.noConflict();

    // _amara may exist with a queue of actions that need to be processed after the
    // embedder has finally loaded. Store the queue in toPush for processing in init().
    var toPush = window._amara || [];

    var Amara = function(Amara) {

        // For reference in inner functions.
        var that = this;

        this.init = function() {

            // If we have a queue from before the embedder loaded, process the actions.
            if (toPush) {
                for (var i = 0; i < toPush.length; i++) {
                    that.push(toPush[i]);
                }
                toPush = [];
            }
        };

        // push() handles all action calls before and after the embedder is loaded.
        this.push = function(args) {

            // Must only send push() an object with only two arguments:
            //     * Action  (string)
            //     * Options (object or string)
            //
            // Note: we don't use traditional function arguments because before the
            // embedder is loaded, _amara is just an array with a normal push() method.
            if (arguments[0].length === 2) {

                var action = args[0];
                var options = args[1];

                // If a method exists for this action, call it with the options.
                if (that[action]) {
                    that[action](options);
                }
            }

        };

        // The core function for constructing an entire video with Amara subtitles from
        // just a video URL. This includes DOM creation for the video, etc.
        this.embedVideo = function(videoURL) {
            console.log(videoURL);
        };

    };

    window._amara = new Amara();
    window._amara.init();

}(window, document));
