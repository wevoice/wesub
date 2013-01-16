from django import template
from django.utils.translation import (
    get_language_info, gettext_lazy as _
)


import logging
logger = logging.getLogger('utils.languagetags')



register = template.Library()

@register.filter()
def to_localized_display(language_code):
    '''
    Translates from a language code to the language name
    in the locale the user is viewing the site. For example:
    en -> Anglaise (if user is viewing with 'fr'
    en -> English
    It uses the django internal machinery to figure out what
    language the request cicle is in, currently set on the
    localurl middleware.
    IF anything is wrong, will log the missing error and
    will return a '?'.
    '''
    try:
        return _(get_language_info(unicode(language_code))['name_local'].encode('utf-8'))
    except KeyError:
        logger.error('Uknown language code to be translated', extra={
            'language_code': unicode(language_code),
        })
    return '?'

