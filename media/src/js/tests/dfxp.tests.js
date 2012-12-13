describe('DFXP', function() {

    var parser = new AmaraDFXPParser();

    describe('#init()', function() {
        it('should initialize a set of mock subtitles', function() {

            // Initialize the parser with a sample XML string.
            parser.init(sampleXmlString);

            // Our sample set of subtitles should contain 1,919 subtitles.
            expect(parser.getSubtitles().length).toBe(1919);

        });
    });
});
