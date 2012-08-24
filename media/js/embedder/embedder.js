(function(window, document, undefined) {

    // When the embedder is compiled, dependencies will be loaded directly before this
    // function. Set dependencies to use no-conflict mode to avoid destroying any
    // original objects.
    var __ = _.noConflict();
    var _$ = Zepto;
    var _Backbone = Backbone.noConflict();
    var _Popcorn = Popcorn.noConflict();

    // _amara may exist with a queue of actions that need to be processed after the
    // embedder has finally loaded. Store the queue in toPush for processing in init().
    var toPush = window._amara || [];

    var Amara = function(Amara) {

        // For reference in inner functions.
        var that = this;

        // This will store all future instances of Amara-powered videos.
        // I'm trying really hard here to not use the word "widget".
        this.amaraInstances = [];

        // Private methods that are called via the push() method.
        var actions = {

            // The core function for constructing an entire video with Amara subtitles from
            // just a video URL. This includes DOM creation for the video, etc.
            embedVideo: function(options) {

                // Make sure we have a URL to work with.
                // If we do, init a new Amara view.
                if (__.has(options, 'url') && __.has(options, 'div')) {

                    that.amaraInstances.push(
                        new that.AmaraView({

                            // TODO: This needs to support a node OR ID string.
                            el: _$(options.div)[0],
                            model: new VideoModel(options)
                        })
                    );
                }
            }
        };

        // Utilities.
        var utils = {
            parseFloatAndRound: function(val) {
                return (Math.round(parseFloat(val) * 100) / 100).toFixed(2);
            }
        };

        // Video model.
        var VideoModel = _Backbone.Model.extend({

            // The initialization of these vars is unnecessary, but it's nice to know
            // what vars will *eventually* be on the video model.

            // This var will be true once we've retrieved the rest of the model attrs
            // from the Amara API.
            is_complete: false,

            // Set from within the embedder.
            div: '',
            height: '',
            initial_language: null,
            is_on_amara: null,
            subtitles: [], // Backbone collection
            url: '',
            width: '',

            // Set from the Amara API
            all_urls: [],
            created: null,
            description: null,
            duration: null,
            id: null,
            languages: [],
            original_language: null,
            project: null,
            resource_uri: null,
            team: null,
            thumbnail: null,
            title: null,

            // Every time a video model is created, do this.
            initialize: function() {

                var video = this;
                var apiURL = 'https://staging.universalsubtitles.org/api2/partners/videos/?&video_url=';

                this.subtitles = new that.Subtitles();

                // Make a call to the Amara API to get attributes like available languages,
                // internal ID, description, etc.
                _$.ajax({
                    url: apiURL + this.get('url'),
                    dataType: 'jsonp',
                    success: function(resp) {

                        if (resp.objects.length) {

                            // The video exists on Amara.
                            video.set('is_on_amara', true);

                            // There should only be one object.
                            if (resp.objects.length === 1) {

                                // Set all of the API attrs as attrs on the video model.
                                video.set(resp.objects[0]);

                                // Set the initial language to either the one provided by the initial
                                // options, or the original language from the API.
                                video.set('initial_language',
                                    video.get('initial_language') ||
                                    video.get('original_language')
                                );
                            }

                        } else {

                            // The video does not exist on Amara.
                            video.set('is_on_amara', false);

                        }

                        // Mark that the video model has been completely populated.
                        video.set('is_complete', true);
                    }
                });
            }
        });

        // SubtitleSet model.
        var SubtitleSet = _Backbone.Model.extend({

            // Set from the Amara API
            description: null,
            language: null,
            note: null,
            resource_uri: null,
            site_url: null,
            sub_format: null,
            subtitles: [],
            title: null,
            version_no: null,
            video: null,
            video_description: null,
            video_title: null

        });

        // Subtitles collection.
        this.Subtitles = _Backbone.Collection.extend({
            model: SubtitleSet
        });

        // Amara view. This contains all of the events and logic for a single instance of
        // an Amara-powered video.
        this.AmaraView = _Backbone.View.extend({

            initialize: function() {
                this.model.view = this;
                this.template = __.template(this.templateHTML);
                this.render();
            },

            events: {
                'click ul.amara-languages-list a': 'changeLanguage',
                'click a.amara-current-language':  'languageButtonClicked',
                'click a.amara-share-button':      'shareButtonClicked',
                'click a.amara-transcript-button': 'toggleTranscriptDisplay',
                'click a.amara-subtitles-button':  'toggleSubtitlesDisplay'
            },

            render: function() {
                
                var that = this;

                // Create a container that we will use to inject the Popcorn video.
                this.$el.prepend('<div class="amara-popcorn"></div>');

                this.$popContainer = $('div.amara-popcorn', this.$el);

                // Copy the width and height to the new Popcorn container.
                this.$popContainer.width(this.$el.width());
                this.$popContainer.height(this.$el.height());

                // This is a hack until Popcorn.js supports passing a DOM elem to
                // its smart() method. See: http://bit.ly/L0Lb7t
                var id = 'amara-popcorn-' + Math.floor(Math.random() * 100000000);
                this.$popContainer.attr('id', id);

                // Reset the height on the parent amara-embed div. If we don't do this,
                // our amara-tools div won't be visible.
                this.$el.height('auto');

                // Init the Popcorn video.
                this.pop = _Popcorn.smart(this.$popContainer.attr('id'), this.model.get('url'));

                this.pop.on('loadedmetadata', function() {

                    // Set the video model's height and width, now that we know it.
                    that.model.set('height', that.pop.position().height);
                    that.model.set('width', that.pop.position().width);

                    // Create the actual core DOM for the Amara container.
                    that.$el.append(that.template({
                        video_url: 'http://staging.universalsubtitles.org/en/videos/' + that.model.get('id'),
                        width: that.model.get('width')
                    }));

                    // Just set some cached Zepto selections for later use.
                    that.cacheNodes();

                    // Wait until we have a complete video model (the API was hit as soon as
                    // the video instance was created), and then retrieve the initial set
                    // of subtitles, so we can begin building out the transcript viewer
                    // and the subtitle display.
                    //
                    // We could just make this a callback on the model's initialize() for
                    // after we get a response, but there may be cases where we want to init
                    // a VideoModel separately from an AmaraView.
                    that.waitUntilVideoIsComplete(
                        function() {

                            // Grab the subtitles for the initial language and do yo' thang.
                            if (that.model.get('is_on_amara')) {

                                // Build the language selection dropdown menu.
                                that.buildLanguageSelector();

                                // Make the request to fetch the initial subtitles.
                                //
                                // TODO: This needs to be an option.
                                that.fetchSubtitles(that.model.get('initial_language'), function() {

                                    // When we've got a response with the subtitles, start building
                                    // out the transcript viewer and subtitles.
                                    that.buildTranscript(that.model.get('initial_language'));
                                    that.buildSubtitles(that.model.get('initial_language'));
                                });
                            } else {
                                // Do some other stuff for videos that aren't yet on Amara.
                            }
                        }
                    );
                });

                return this;

            },

            // View utilities. I would like to make these utilities as independent as possible.
            // If someone wants to create a "headless" AmaraView, they should be able to use
            // these utilities without a DOM structure. There's work to be done here to
            // support that cause.
            buildLanguageSelector: function() {
                var langs = this.model.get('languages');
                if (langs.length) {
                    for (var i = 0; i < langs.length; i++) {
                        this.$amaraLanguagesList.append('' +
                            '<li>' +
                                '<a href="#" data-language="' + langs[i].code + '">' +
                                    langs[i].name +
                                '</a>' +
                            '</li>');
                    }
                } else {
                    // We have no languages.
                }
            },
            buildSubtitles: function(language) {

                // Remove any existing subtitle events.
                this.pop.removeTrackEvent('amarasubtitle');

                // Get the subtitle sets for this language.
                var subtitleSets = this.model.subtitles.where({'language': language});

                if (subtitleSets.length) {
                    var subtitleSet = subtitleSets[0];

                    // Get the actual subtitles for this language.
                    var subtitles = subtitleSet.get('subtitles');

                    // For each subtitle, init the Popcorn subtitle plugin.
                    for (var i = 0; i < subtitles.length; i++) {
                        this.pop.amarasubtitle({
                            start: subtitles[i].start,
                            end: subtitles[i].end,
                            text: subtitles[i].text
                        });
                    }

                    this.$popSubtitlesContainer = $('div.amara-popcorn-subtitles', this.$el);

                    this.$amaraCurrentLang.text(this.getLanguageNameForCode(subtitleSet.get('language')));
                }
            },
            buildTranscript: function(language) {

                // Remove any existing transcript events.
                this.pop.removeTrackEvent('amaratranscript');

                var subtitleSet;

                // Get the subtitle sets for this language.
                var subtitleSets = this.model.subtitles.where({'language': language});

                if (subtitleSets.length) {
                    subtitleSet = subtitleSets[0];
                } else {
                    $('.amara-transcript-line-right', this.$transcriptBody).text('No subtitles available.');
                }

                // Get the actual subtitles for this language.
                var subtitles = subtitleSet.get('subtitles');

                if (subtitles.length) {

                    // Remove the loading indicator.
                    this.$transcriptBody.html('');

                    // For each subtitle, init the Popcorn transcript plugin.
                    for (var i = 0; i < subtitles.length; i++) {
                        this.pop.amaratranscript({
                            start: subtitles[i].start,
                            start_clean: utils.parseFloatAndRound(subtitles[i].start),
                            start_of_paragraph: subtitles[i].start_of_paragraph,
                            end: subtitles[i].end,
                            text: subtitles[i].text,
                            container: this.$transcriptBody.get(0)
                        });
                    }

                    this.$amaraCurrentLang.text(this.getLanguageNameForCode(subtitleSet.get('language')));

                } else {
                    $('.amara-transcript-line-right', this.$transcriptBody).text('No subtitles available.');
                }
            },

            // This is a temporary utility function to grab a language's name from a language
            // code. We won't need this once we update our API to return the language name
            // with the subtitles.
            // See https://unisubs.sifterapp.com/projects/12298/issues/722972/comments
            getLanguageNameForCode: function(languageCode) {
                var languages = this.model.get('languages');
                var language = __.find(languages, function(l) { return l.code === languageCode; });
                return language.name;
            },

            // Make a call to the Amara API and retrieve a set of subtitles for a specific
            // video in a specific language. When we get a response, add the subtitle set
            // to the video model's 'subtitles' collection for later retrieval by language code.
            fetchSubtitles: function(language, callback) {
                var that = this;

                var apiURL = ''+
                    'https://staging.universalsubtitles.org/api2/partners/videos/' +
                    this.model.get('id') + '/languages/' + language + '/subtitles/';

                // Make a call to the Amara API to retrieve subtitles for this language.
                //
                // TODO: If we already have subtitles in this language, don't do anything.
                _$.ajax({
                    url: apiURL,
                    dataType: 'jsonp',
                    success: function(resp) {

                        // Save these subtitles to the video's 'subtitles' collection.

                        // TODO: Placeholder until we have the API return the language code.
                        resp.language = language;
                        that.model.subtitles.add(
                            new SubtitleSet(resp)
                        );

                        // Call the callback.
                        callback(resp);
                    }
                });
            },

            // View methods. These are methods that are used with the full AmaraView.
            changeLanguage: function(e) {

                var that = this;
                var lang = $(e.target).data('language');

                this.fetchSubtitles(lang, function() {
                    that.buildTranscript(lang);
                    that.buildSubtitles(lang);
                });

                this.$amaraLanguagesList.hide();
                return false;
            },
            languageButtonClicked: function() {
                this.$amaraLanguagesList.toggle();
                return false;
            },
            shareButtonClicked: function() {
                return false;
            },
            toggleSubtitlesDisplay: function() {

                // TODO: This button needs to be disabled unless we have subtitles to toggle.
                this.$popSubtitlesContainer.toggle();
                this.$subtitlesButton.toggleClass('amara-button-enabled');
                return false;
            },
            toggleTranscriptDisplay: function() {

                // TODO: This button needs to be disabled unless we have a transcript to toggle.
                this.$amaraTranscript.toggle();
                this.$transcriptButton.toggleClass('amara-button-enabled');
                return false;
            },

            waitUntilVideoIsComplete: function(callback) {

                var that = this;

                // is_complete gets set as soon as the initial API call to build out the video
                // instance has finished.
                if (!this.model.get('is_complete')) {
                    setTimeout(function() { that.waitUntilVideoIsComplete(callback); }, 100);
                } else {
                    callback();
                }
            },

            templateHTML: '' +
                '<div class="amara-tools" style="width: {{ width }}px;">' +
                '    <div class="amara-bar amara-group">' +
                //'        <a href="#" class="amara-share-button amara-button"></a>' +
                '        <a href="{{ video_url }}" target="blank" class="amara-logo amara-button">Amara</a>' +
                '        <ul class="amara-displays amara-group">' +
                '            <li><a href="#" class="amara-transcript-button amara-button"></a></li>' +
                '            <li><a href="#" class="amara-subtitles-button amara-button"></a></li>' +
                '        </ul>' +
                '        <div class="amara-languages">' +
                '            <a href="#" class="amara-current-language">Loading&hellip;</a>' +
                '            <ul class="amara-languages-list"></ul>' +
                '        </div>' +
                '    </div>' +
                '    <div class="amara-transcript">' +
                '        <div class="amara-transcript-header amara-group">' +
                //'            <div class="amara-transcript-header-left">' +
                //'                Auto-stream <span>OFF</span>' +
                //'            </div>' +
                //'            <div class="amara-transcript-header-right">' +
                //'                <form action="" class="amara-transcript-search">' +
                //'                    <input class="amara-transcript-search-input" placeholder="Search transcript" />' +
                //'                </form>' +
                //'            </div>' +
                '        </div>' +
                '        <div class="amara-transcript-body">' +
                '            <a href="#" class="amara-transcript-line amara-group">' +
                '                <span class="amara-transcript-line">' +
                '                    Loading transcript&hellip;' +
                '                </span>' +
                '            </a>' +
                '        </div>' +
                '    </div>' +
                '</div>',

            cacheNodes: function() {
                this.$amaraTools         = $('div.amara-tools',      this.$el);
                this.$amaraBar           = $('div.amara-bar',        this.$amaraTools);
                this.$amaraTranscript    = $('div.amara-transcript', this.$amaraTools);

                this.$amaraDisplays      = $('ul.amara-displays',         this.$amaraTools);
                this.$transcriptButton   = $('a.amara-transcript-button', this.$amaraDisplays);
                this.$subtitlesButton    = $('a.amara-subtitles-button',  this.$amaraDisplays);

                this.$amaraLanguages     = $('div.amara-languages',       this.$amaraTools);
                this.$amaraCurrentLang   = $('a.amara-current-language',  this.$amaraLanguages);
                this.$amaraLanguagesList = $('ul.amara-languages-list',  this.$amaraLanguages);

                this.$transcriptBody     = $('div.amara-transcript-body', this.$amaraTranscript);
            }

        });

        // push() handles all action calls before and after the embedder is loaded.
        // Aside from init(), this is the only function that may be called from the
        // parent document.
        //
        // Must send push() an object with only two items:
        //     * Action  (string)
        //     * Options (object)
        //
        // Note: we don't use traditional function arguments because before the
        // embedder is loaded, _amara is just an array with a normal push() method.
        this.push = function(args) {
            
            // No arguments? Don't do anything.
            if (!arguments.length) { return; }

            // Must send push() an object with only two items.
            if (__.size(arguments[0]) === 2) {

                var action = args[0];
                var options = args[1];

                // If a method exists for this action, call it with the options.
                if (actions[action]) {
                    actions[action](options);
                }
            }

        };

        // init() gets called as soon as the embedder has finished loading.
        // Simply processes the existing _amara queue if we have one.
        this.init = function() {

            // Load the Amara CSS.
            var tag = document.getElementsByTagName('script')[0];
            var style = document.createElement('link');
            style.rel = 'stylesheet';
            style.type = 'text/css';

            // TODO: This needs to be a production URL based on DEBUG or not.
            style.href = '/site_media/css/embedder/amara.css';
            tag.parentNode.insertBefore(style, tag);

            // Change the template delimiter for Underscore templates.
            __.templateSettings = { interpolate : /\{\{(.+?)\}\}/g };

            // If we have a queue from before the embedder loaded, process the actions.
            if (toPush) {
                for (var i = 0; i < toPush.length; i++) {
                    that.push(toPush[i]);
                }
                toPush = [];
            }

            // Check to see if we have any amara-embed's to initilize.
            var amaraEmbeds = _$('div.amara-embed');

            if (amaraEmbeds.length) {
                amaraEmbeds.each(function() {

                    var $div = $(this);

                    // Call embedVideo with this div and URL.
                    that.push(['embedVideo', {
                        'div': this,
                        'initial_language': $div.data('initial-language'),
                        'url': $div.data('url')
                    }]);
                });
            }

        };

    };

    window._amara = new Amara();
    window._amara.init();

}(window, document));
