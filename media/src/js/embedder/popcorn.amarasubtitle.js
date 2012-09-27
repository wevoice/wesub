(function (Popcorn) {

    // TODO: Document the hell out of this.

    var i = 0;
    var createDefaultContainer = function(context, id) {

        var ctxContainer = context.container = document.createElement('div');
        var style = ctxContainer.style;
        var media = context.media;

        ctxContainer.id = id || Popcorn.guid();
        ctxContainer.className = 'amara-popcorn-subtitles';

        style.width = media.offsetWidth + 'px';

        context.media.parentNode.childNodes[0].appendChild(ctxContainer);

        return ctxContainer;
    };

    Popcorn.plugin('amarasubtitle', {
        _setup: function(options) {
            var newdiv = document.createElement('div');

            newdiv.id = 'subtitle-' + i++;
            newdiv.style.display = 'none';

            // Creates a div for all subtitles to use
            if (!this.container && (!options.target || options.target === 'subtitle-container')) {
                createDefaultContainer(this);
            }

            // if a target is specified, use that
            if (options.target && options.target !== 'subtitle-container') {
                // In case the target doesn't exist in the DOM
                options.container = document.getElementById(options.target) || createDefaultContainer(this, options.target);
            } else {
                // use shared default container
                options.container = this.container;
            }

            if (document.getElementById(options.container.id)) {
                document.getElementById(options.container.id).appendChild(newdiv);
            }
            options.innerContainer = newdiv;

            options.showSubtitle = function() {
                options.innerContainer.innerHTML = options.text || '';
            };
        },
        start: function(event, options){
            options.innerContainer.style.display = 'block';
            options.showSubtitle(options, options.text);
        },
        end: function(event, options) {
            options.innerContainer.style.display = 'none';
            options.innerContainer.innerHTML = '';
        },
        _teardown: function (options) {
            options.container.removeChild(options.innerContainer);
        }
    });
})(Popcorn);
