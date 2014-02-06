var Popcorn = Popcorn || null;

(function (Popcorn) {

    var i = 0;
    var newdiv;

    var createDefaultContainer = function(context, id) {
        var ctxContainer = context.container = document.createElement('div');
        var style = ctxContainer.style;
        ctxContainer.id = id || Popcorn.guid();
        ctxContainer.className = 'amara-popcorn-subtitles';

        style.width = '100%';
        
        // I do not know why the media node and its parents get the same id but
        // seem to be different with Youtube media, so checking this for now
        if ((context.media.nodeName == 'VIDEO') ||
           (context.media.id == context.media.parentNode.id))
            context.media.parentNode.appendChild(ctxContainer);
        else
            context.media.appendChild(ctxContainer);

        newdiv = document.createElement('div');
        newdiv.id = Popcorn.guid('subtitle-');
        newdiv.style.display = 'none';
        ctxContainer.appendChild(newdiv);
        return ctxContainer;
    };

    Popcorn.plugin('amarasubtitle', {
        _setup: function(options) {
            // Creates a div for all subtitles to use
            if (!this.container && (!options.target || options.target === 'subtitle-container')) {
                createDefaultContainer(this);
            }
        },
        start: function(event, options){
            // popcorn will call start on two ocasions:
            // - on startup, where options.id is set
            // - during playback, where options id is not set
            // we only need to change the text at that time, so:
            if (!options.id &&options.text !== '') {
                newdiv.style.display = 'inline-block';
                newdiv.innerHTML = options.text || '';
            }
        },
        end: function(event, options) {
            newdiv.style.display = 'none';
        },
        _update: function(event, newOptions) {
            newdiv.innerHTML = event.text = newOptions.text;

            if (newOptions.text === '') {
                newdiv.style.display = 'none';
            } else {
                newdiv.style.display = 'inline-block';
            }
        },
        _teardown: function (options) {
            options.container.removeChild(options.innerContainer);
        }
    });
})(Popcorn);
