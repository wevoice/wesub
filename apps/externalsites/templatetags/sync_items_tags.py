import json
from django.conf import settings
from django.template.defaulttags import register
from django.utils.safestring import mark_safe

ALL_LANGUAGES_DICT = dict(settings.ALL_LANGUAGES)

@register.filter
def get_fields(dictionary):
    output = []
    dict = json.loads(dictionary)
    output.append(dict['account_type'])
    output.append(mark_safe('<a href="' +
                            dict['video_url'] +
                            '">Go to Video</a>'))
    language = language_code = dict['language']
    if language_code in ALL_LANGUAGES_DICT:
        language = ALL_LANGUAGES_DICT[language_code]
    output.append(language)
    output.append(dict['details'])
    return output
