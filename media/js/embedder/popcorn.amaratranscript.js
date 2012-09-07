(function (Popcorn) {

    // Scroll the transcript container to the line, and bring the line to the center
    // of the vertical height of the container.
    function scrollToLine(options) {

        // Grab the DOM lib.
        var _$ = options._$;

        // Retrieve the absolute positions of the line and the container.
        var linePos = _$(options.line).offset();
        var containerPos = _$(options.container).offset();

        // The difference in top-positions between the line and the container.
        var diffY = linePos.top - containerPos.top;

        // The available vertical space within the container.
        var spaceY = options.container.clientHeight - options.line.offsetHeight;

        // Set the scrollTop of the container to the difference in top-positions,
        // plus the existing scrollTop, minus 50% of the available vertical space.
        var scrollTop = options.container.scrollTop;
        scrollTop += diffY - spaceY / 2;
        options.container.scrollTop = scrollTop;
    }
    
    Popcorn.plugin('amaratranscript', {
        _setup : function(options) {

            options.pop = this;

            // Construct the transcript line.
            options.line = document.createElement('a');
            options.line.href = '#';
            options.line.classList.add('amara-transcript-line');
            options.line.innerHTML = options.text;

            // If this subtitle has indicated that it's the beginning of a paragraph,
            // prepend two line breaks before the subtitle.
            if (options.start_of_paragraph) {
                options.container.appendChild(document.createElement('br'));
                options.container.appendChild(document.createElement('br'));
            }

            // Add the subtitle to the transcript container.
            options.container.appendChild(options.line);

            // Upon clicking the line, we should set the video playhead to this line's
            // start time.
            options.line.addEventListener('click', function(e) {
                options.pop.currentTime(options.start);
                e.preventDefault();
                e.stopPropagation();
            }, false);

        },
        start: function(event, options){

            // When we reach this subtitle, add this class.
            options.line.classList.add('current-subtitle');

            scrollToLine(options);
        },
        end: function(event, options){

            // When we're no longer on this subtitle, remove this class.
            options.line.classList.remove('current-subtitle');
        },
        _teardown: function(options, start) {
            options.container.removeChild(options.line);
        }
    });
})(Popcorn);
