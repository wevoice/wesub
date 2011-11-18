$(function() {
    // Store commonly used elements
    var languageSelector = $(".language-selector select");
    var typeSelector = $(".type-selector select");

    // Filter the language list based on what type of task is selected
    var filterLanguages = function() {
        var step = typeSelector.find(":selected").text();
        var langs;

        if (step === 'Review') {
            langs = reviewableLanguages;
        } else if (step === 'Approve') {
            langs = approvableLanguages;
        } else if (step === 'Translate') {
            langs = translatableLanguages;
        } else if (step === 'Subtitle') {
            $('.language-selector').hide();
            languageSelector.val('');
            return;
        }

        $('.language-selector').show();
        languageSelector.html('<option value=""></option>');

        _(languageChoices).chain().filter(function(choice) {
            return _.contains(langs, choice[0]);
        }).each(function(choice) {
            languageSelector.append('<option value=' + choice[0] + '>' + choice[1] + '</option>');
        });

        languageSelector.trigger('liszt:updated');
    };

    // Bind events
    typeSelector.change(function(e) {
        filterLanguages();
    });

    // Disable invalid task types
    if (_.isEmpty(reviewableLanguages)) {
        typeSelector.find(':contains("Review")').attr('disabled', 'disabled');
    }
    if (_.isEmpty(approvableLanguages)) {
        typeSelector.find(':contains("Approve")').attr('disabled', 'disabled');
    }
    if (_.isEmpty(translatableLanguages)) {
        typeSelector.find(':contains("Translate")').attr('disabled', 'disabled');
    }
    if (!subtitlable) {
        typeSelector.find(':contains("Subtitle")').attr('disabled', 'disabled');
    }

    // Select the first valid task type
    // TODO: Handle case where no types are valid (e.g.: subtitling in progress)
    typeSelector.find('option').each(function(idx) {
        var option = $(this);

        if (!option.attr('disabled')) {
            option.parent('select').val(option.val());
            return false;
        }
    });
    var nothing_enabled = _.all(typeSelector.find('option').get(), function(el) {
        return !!$(el).attr('disabled');
    });
    if (nothing_enabled) {
        typeSelector.hide();
        $('.submit').hide();
        $('.cannot-create').show();
    }

    // Chosenify select elements
    $(".chosen select").chosen();

    // Perform initial filtering
    filterLanguages();
});
