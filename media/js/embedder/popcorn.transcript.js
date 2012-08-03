(function (Popcorn) {
    Popcorn.plugin( 'transcript' , {
        _setup : function(options) {

            options.pop = this;
            options.lineHtml = document.createElement('a');
            options.lineHtml.href = '#';
            options.lineHtml.classList.add('amara-group');
            options.lineHtml.classList.add('amara-transcript-line');

            var lineTemplate = '' +
                '<span class="amara-transcript-line-left">' + options.start_clean + '</span>' +
                '<span class="amara-transcript-line-right">' + options.text + '</span>';

            options.lineHtml.innerHTML = lineTemplate;
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
        frame: function(event, options) {

        },
        toString: function(event, options) {

        } 
    });
})(Popcorn);
