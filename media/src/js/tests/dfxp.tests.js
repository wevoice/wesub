describe('dfxpToMarkdown', function() {
    function callDFXPToMarkdown(dfxpString) {
        return dfxp.dfxpToMarkdown($(dfxpString)[0]);
    }
    it('leaves simple text alone', function() {
        expect(callDFXPToMarkdown('<p>simple text</p>')).toBe('simple text');
    });
    it('converts bold spans', function() {
        var dfxpString = '<p><span tts:fontWeight="bold">text</span></p>';
        expect(callDFXPToMarkdown(dfxpString)).toBe('**text**');
    });
    it('converts italic spans', function() {
        var dfxpString = '<p><span tts:fontStyle="italic">text</span></p>';
        expect(callDFXPToMarkdown(dfxpString)).toBe('*text*');
    });
    it('converts underline spans', function() {
        var dfxpString = '<p><span tts:textDecoration="underline">text</span></p>';
        expect(callDFXPToMarkdown(dfxpString)).toBe('_text_');
    });
    it('converts BRs:', function() {
        var dfxpString = '<p>line1<br />line2</p>';
        expect(callDFXPToMarkdown(dfxpString)).toBe('line1\nline2');
    });
    it('handles lowercase attributes', function() {
        var dfxpString = '<p><span tts:textdecoration="underline">text</span></p>';
        expect(callDFXPToMarkdown(dfxpString)).toBe('_text_');
    });
    it('handles attributes without tts:', function() {
        var dfxpString = '<p><span textDecoration="underline">text</span></p>';
        expect(callDFXPToMarkdown(dfxpString)).toBe('_text_');
    });
    it('handles nested spans:', function() {
        var dfxpString = ('<p><span textDecoration="underline">underline ' +
            '<span fontWeight="bold">bold</span></span></p>)');
        expect(callDFXPToMarkdown(dfxpString)).toBe('_underline **bold**_');
    });
    it('handles BRs nested in spans:', function() {
        var dfxpString = ('<p><span textDecoration="underline">line1' +
            '<br />line2</span></p>)');
        expect(callDFXPToMarkdown(dfxpString)).toBe('_line1\nline2_');
    });
});

