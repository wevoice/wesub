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
        },
        end: function(event, options){
            options.lineHtml.classList.remove('current-subtitle');
        },
        _teardown: function (options, start) {
            options.container.removeChild(options.lineHtml);
        }
    });
})(Popcorn);
