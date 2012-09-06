(function (Popcorn) {
    Popcorn.plugin('amaratranscript', {
        _setup : function(options) {

            options.pop = this;
            options.lineHtml = document.createElement('a');
            options.lineHtml.href = '#';
            options.lineHtml.classList.add('amara-transcript-line');
            options.lineHtml.innerHTML = options.text;

            if (options.start_of_paragraph) {
                options.container.appendChild(document.createElement('br'));
                options.container.appendChild(document.createElement('br'));
            }

            options.container.appendChild(options.lineHtml);

            options.lineHtml.addEventListener('click', function(e) {
                options.pop.currentTime(options.start);
                e.preventDefault();
                e.stopPropagation();
            }, false);

        },
        start: function(event, options){
            options.lineHtml.classList.add('current-subtitle');

            // This needs to be whether or not we're currently forcing the
            // current line to come to center.
            if (true) {
                var verticalSpace = options.container.clientHeight - options.lineHtml.offsetHeight;
                var scrollTop = whatever - (veticalSpace / 2);
            }
        },
        end: function(event, options){
            options.lineHtml.classList.remove('current-subtitle');
        },
        _teardown: function(options, start) {
            options.container.removeChild(options.lineHtml);
        }
    });
})(Popcorn);
