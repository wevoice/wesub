describe('Test the SubtitleList class', function() {
    var subtitleList = null;

    beforeEach(function() {
        module('amara.SubtitleEditor.subtitles.models');
    });

    beforeEach(inject(function(SubtitleList) {
        subtitleList = new SubtitleList();
        subtitleList.loadEmptySubs('en');

        this.addMatchers({
            'toHaveTimes': function(startTime, endTime) {
                return (this.actual.startTime == startTime &&
                    this.actual.endTime == endTime);
            },
        });
    }));

    it('should start empty', function() {
        expect(subtitleList.subtitles).toEqual([]);
    });

    it('should support insertion and removal', function() {
        var sub1 = subtitleList.insertSubtitleBefore(null);
        var sub2 = subtitleList.insertSubtitleBefore(sub1);
        var sub3 = subtitleList.insertSubtitleBefore(null);
        expect(subtitleList.subtitles).toEqual([sub2, sub1, sub3]);
        subtitleList.removeSubtitle(sub1);
        expect(subtitleList.subtitles).toEqual([sub2, sub3]);
        subtitleList.removeSubtitle(sub2);
        expect(subtitleList.subtitles).toEqual([sub3]);
        subtitleList.removeSubtitle(sub3);
        expect(subtitleList.subtitles).toEqual([]);
    });

    it('should update content', function() {
        var sub1 = subtitleList.insertSubtitleBefore(null);
        expect(sub1.content()).toEqual('');
        subtitleList.updateSubtitleContent(sub1, 'test');
        expect(sub1.content()).toEqual('test');
        subtitleList.updateSubtitleContent(sub1, '*test*');
        expect(sub1.content()).toEqual('<i>test</i>');
        subtitleList.updateSubtitleContent(sub1, '**test**');
        expect(sub1.content()).toEqual('<b>test</b>');
    });

    it('should update timing', function() {
        var sub1 = subtitleList.insertSubtitleBefore(null);
        var sub2 = subtitleList.insertSubtitleBefore(null);
        expect(subtitleList.syncedCount).toEqual(0);
        subtitleList.updateSubtitleTime(sub1, 500, 1500);
        expect(sub1).toHaveTimes(500, 1500);
        expect(subtitleList.syncedCount).toEqual(1);
        subtitleList.updateSubtitleTime(sub1, 1000, 1500);
        expect(sub1).toHaveTimes(1000, 1500);
        expect(subtitleList.syncedCount).toEqual(1);
        subtitleList.updateSubtitleTime(sub2, 2000, 2500);
        expect(sub2).toHaveTimes(2000, 2500);
        expect(subtitleList.syncedCount).toEqual(2);
    });

    it('should invoke change callbacks', function() {
        var handler = jasmine.createSpyObj('handler', ['onChange']);
        subtitleList.addChangeCallback(handler.onChange);

        var sub = subtitleList.insertSubtitleBefore(null);
        expect(handler.onChange.callCount).toEqual(1);
        expect(handler.onChange).toHaveBeenCalledWith({
            type: 'insert',
            subtitle: sub,
            before: null,
        });

        subtitleList.updateSubtitleTime(sub, 500, 1500);
        expect(handler.onChange.callCount).toEqual(2);
        expect(handler.onChange).toHaveBeenCalledWith({
            type: 'update',
            subtitle: sub,
        });

        subtitleList.updateSubtitleContent(sub, 'content');
        expect(handler.onChange.callCount).toEqual(3);
        expect(handler.onChange).toHaveBeenCalledWith({
            type: 'update',
            subtitle: sub,
        });

        subtitleList.removeSubtitle(sub);
        expect(handler.onChange.callCount).toEqual(4);
        expect(handler.onChange).toHaveBeenCalledWith({
            type: 'remove',
            subtitle: sub,
        });

        subtitleList.removeChangeCallback(handler.onChange);
        var sub2 = subtitleList.insertSubtitleBefore(null);
        subtitleList.updateSubtitleTime(sub2, 500, 1500);
        subtitleList.updateSubtitleContent(sub2, 'content');
        subtitleList.removeSubtitle(sub2);
        expect(handler.onChange.callCount).toEqual(4);
    });
});

