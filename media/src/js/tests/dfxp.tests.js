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

                var xml = AmarajQuery.parseXML("<rss><channel></channel></rss>");
                expect(parser.utils.xmlToString(xml)).toBe('<rss><channel/></rss>');

            });
        });
    });
});
