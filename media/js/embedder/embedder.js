(function(window, document, undefined) {

    var toPush = window._amara || [];

    var Amara = function(Amara) {

        var that = this;

        this.push = function(args) {

            if (arguments[0].length === 2) {
                // Must only send push() an object with two arguments:
                //     - Method  (string)
                //     - Options (object or string)

                var method = args[0];
                var options = args[1];

                if (that[method]) {
                    that[method](options);
                }
            }

        };
        this.init = function() {
            if (toPush) {
                for (var i = 0; i < toPush.length; i++) {
                    that.push(toPush[i]);
                }
                toPush = [];
            }
        };

        this.embedVideo = function(videoURL) {
            console.log(videoURL);
        };

    };

    window._amara = new Amara();
    window._amara.init();

}(window, document));
