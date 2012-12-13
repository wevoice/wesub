describe('DFXP', function() {

    var parser = new AmaraDFXPParser();

    describe('#init()', function() {
        it('should initialize a set of mock subtitles', function() {

            // Initialize the parser with a sample XML string.
            parser.init(sampleXmlString);

            // Our sample set of subtitles should contain 1,919 subtitles.
            expect(parser.getSubtitles().length).toBe(1919);

        });
        it('should convert DFXP-style formatting to Markdown', function() {
            // The very last subtitle has DFXP-style formatting that should've
            // been converted to Markdown.

            var lastSubtitle = parser.getLastSubtitle();
            var content = parser.content(lastSubtitle);

            expect(content).toBe('♪ [Touching **Evil** closing theme music] ♪');

        });
        it('should store two separate instances of XML', function() {
            // The original XML and the working XML should not be the same
            // object.

            expect(parser.$originalXml === parser.$xml).toBe(false);

        });
        it('should convert time expressions to milliseconds', function() {
            // If the parser is working correctly, it would have converted
            // '00:00::01.15' to '1150'.

            var firstSubtitle = parser.getFirstSubtitle();
            var startTime = parser.startTime(firstSubtitle);

            expect(startTime).toBe(1150);
        });
        it('should not have introduce differences between the original and working XML', function() {
            expect(parser.changesMade()).toBe(false);
        });
    });
    describe('#utils', function() {
        describe('.leftPad()', function() {
            it('should left-pad a number to the given width with the given char', function() {
                expect(parser.utils.leftPad(1, 2, 0)).toBe('01');
            });
        });
        describe('.millisecondsToTimeExpression()', function() {
            it('should convert milliseconds to a time expression', function() {

                // This utility function uses other utility functions, so it
                // must be scoped properly.
                expect(parser.utils.millisecondsToTimeExpression.call(parser, 1150))
                    .toBe('00:00:01,150');

            });
        });
        describe('.rightPad()', function() {
            it('should right-pad a number to the given width with the given char', function() {
                expect(parser.utils.rightPad(1, 2, 0)).toBe('10');
            });
        });
        describe('.timeExpressionToMilliseconds()', function() {
            it('should convert a time expression to milliseconds', function() {

                // This utility function uses other utility functions, so it
                // must be scoped properly.
                expect(parser.utils.timeExpressionToMilliseconds.call(parser, '00:00:01,150'))
                    .toBe(1150);

            });
        });
        describe('.xmlToString()', function() {
            it('should convert an XML document to a string', function() {

                var xml = AmarajQuery.parseXML('<rss><channel></channel></rss>');
                expect(parser.utils.xmlToString(xml)).toBe('<rss><channel/></rss>');

            });
        });
    });

    describe('#addSubtitle()', function() {
        it('should add a subtitle to the end of the list', function() {

            // Add a new subtitle.
            parser.addSubtitle(null, null, 'A new subtitle at the end.');

            // Get the last subtitle in the list.
            var lastSubtitle = parser.getLastSubtitle();

            expect(parser.content(lastSubtitle)).toBe('A new subtitle at the end.');

            // Expect that changes have now been made to the working copy;
            expect(parser.changesMade()).toBe(true);

        });
        it('should add a subtitle with a begin and end pre-set', function() {

            // Add a new subtitle with a begin and end pre-set.
            parser.addSubtitle(null, {'begin': 1150, 'end': 1160}, 'New subtitle with timing.');

            // Get the last subtitle in the list.
            var lastSubtitle = parser.getLastSubtitle();

            expect(parser.startTime(lastSubtitle)).toBe(1150);
            expect(parser.endTime(lastSubtitle)).toBe(1160);
            expect(parser.content(lastSubtitle)).toBe('New subtitle with timing.');

        });
        it('should add a subtitle after a given subtitle', function() {

            // Add a new subtitle after the first subtitle, with content and
            // begin/end attrs pre-set.
            var newSubtitle = parser.addSubtitle(0,
                {'begin': 1160, 'end': 1170},
                'New subtitle with timing, after the first subtitle.');

            // Get the second subtitle in the list.
            var secondSubtitle = parser.getSubtitle(1).get(0);

            expect(secondSubtitle).toBe(newSubtitle);
            expect(parser.startTime(secondSubtitle)).toBe(1160);
            expect(parser.endTime(secondSubtitle)).toBe(1170);
            expect(parser.content(secondSubtitle)).toBe('New subtitle with timing, after the first subtitle.');

        });
        it('should add a subtitle with blank content if we pass null', function() {

            // Add a new subtitle with 'null' content.
            var newSubtitle = parser.addSubtitle(null, null, null);

            // Get the last subtitle in the list.
            var lastSubtitle = parser.getLastSubtitle();

            expect(parser.content(lastSubtitle)).toBe('');

        });
    });
    describe('#changesMade()', function() {
        it('should indicate that changes have been made', function() {
            // We've made changes previously, so changesMade() should reflect that,
            // now.

            expect(parser.changesMade()).toBe(true);

        });
    });
    describe('#clearAllContent()', function() {
        it('should clear text content from every subtitle', function() {

            // Wipe 'em out.
            parser.clearAllContent();

            // Get all of the subtitles.
            var $subtitles = parser.getSubtitles();

            // Every subtitle's text() value should be an empty string.
            for (var i = 0; i < $subtitles.length; i++) {
                expect($subtitles.eq(i).text()).toBe('');
            }

        });
        it('should not affect subtitle attributes', function() {

            var firstSubtitle = parser.getFirstSubtitle();
            expect(parser.startTime(firstSubtitle)).toNotBe(-1);

        });
    });
    describe('#clearAllTimes()', function() {
        it('should clear timing data from every subtitle', function() {

            // Wipe 'em out.
            parser.clearAllTimes();

            // Get all of the subtitles.
            var $subtitles = parser.getSubtitles();

            // Every subtitle's timing data should be empty.
            for (var i = 0; i < $subtitles.length; i++) {
                var $subtitle = $subtitles.eq(i);
                var startTime = $subtitle.attr('begin');
                var endTime = $subtitle.attr('end');

                // Verify that they've been emptied.
                expect(startTime).toBe('');
                expect(endTime).toBe('');
            }

        });
    });
    describe('#clone()', function() {
        it('should clone this parser and preserve subtitle text', function() {

            // Add a new subtitle with text, since we blew it all away
            // in a previous test.
            parser.addSubtitle(null, null, 'Some text.');

            // Get the last subtitle of the old parser.
            var lastSubtitleOfOldParser = parser.getLastSubtitle();

            // Expect the content to be what we just set it as.
            expect(parser.content(lastSubtitleOfOldParser)).toBe('Some text.');

            // Clone the parser.
            var newParser = parser.clone(true);

            // Get the last subtitle of the cloned parser.
            var lastSubtitleOfNewParser = newParser.getLastSubtitle();

            // Expect the last subtitle of the cloned parser to have the same
            // content as the last subtitle of the old parser.
            expect(newParser.content(lastSubtitleOfNewParser)).toBe('Some text.');

        });
        it('should clone this parser and discard subtitle text', function() {

            // Get the last subtitle of the old parser.
            var lastSubtitleOfOldParser = parser.getLastSubtitle();

            // Expect the content to be what we just set it as.
            expect(parser.content(lastSubtitleOfOldParser)).toBe('Some text.');

            // Clone the parser, this time discarding text.
            var newParser = parser.clone();

            // Get the last subtitle of the cloned parser.
            var lastSubtitleOfNewParser = newParser.getLastSubtitle();

            // Expect the last subtitle of the cloned parser to have the same
            // content as the last subtitle of the old parser.
            expect(newParser.content(lastSubtitleOfNewParser)).toBe('');

        });
    });
    describe('#content()', function() {
        it('should set text content of a subtitle', function() {

            // Get the last subtitle in the list.
            var lastSubtitle = parser.getLastSubtitle();

            parser.content(lastSubtitle, 'Some new text.');

            expect(parser.content(lastSubtitle)).toBe('Some new text.');
        });
        it('should retrieve text content of a subtitle', function() {

            // Get the last subtitle. In the previous test, we changed the
            // content of the last subtitle.
            var lastSubtitle = parser.getLastSubtitle();

            expect(parser.content(lastSubtitle)).toBe('Some new text.');
        });
    });
    describe('#contentRendered()', function() {
        it('should return the rendered HTML content of the subtitle', function() {

            // First, create a subtitle with Markdown formatting.
            var newSubtitle = parser.addSubtitle(null, null, 'Hey **guys!**');

            // The rendered content of this new subtitle should be converted to
            // HTML.
            expect(parser.contentRendered(newSubtitle)).toBe('Hey <b>guys!</b>');

        });
    });
});
