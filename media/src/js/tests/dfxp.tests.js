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
            /*
             * The very last subtitle has DFXP-style formatting that should've
             * been converted to Markdown.
             */

            var lastSubtitle = parser.getLastSubtitle();
            var content = parser.content(lastSubtitle);

            expect(content).toBe('♪ [Touching **Evil** closing theme music] ♪');

        });
        it('should store two separate instances of XML', function() {
            /*
             * The original XML and the working XML should not be the same
             * object.
             */

            expect(parser.$originalXml === parser.$xml).toBe(false);

        });
        it('should convert time expressions to milliseconds', function() {
            /*
             * If the parser is working correctly, it would have converted
             * '00:00::01.15' to '1150'.
             */

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
});
