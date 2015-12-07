# -*- coding: utf-8 -*-
import json
import time

from django.conf import settings
from django.core.cache import cache
from django.utils.http import cookie_date
from django.utils.translation import (
    get_language, get_language_info, ugettext as _
)
from django.utils.translation.trans_real import parse_accept_lang_header
import babel
import pyuca

from unilangs import get_language_name_mapping, LanguageCode

collator = pyuca.Collator()

# A set of all language codes we support.
_supported_languages_map = get_language_name_mapping('unisubs')
_all_languages_map = get_language_name_mapping('internal')
SUPPORTED_LANGUAGE_CODES = set(_supported_languages_map.keys())
ALL_LANGUAGE_CODES = set(_all_languages_map.keys())

SUPPORTED_LANGUAGE_CHOICES = list(sorted(_supported_languages_map.items(),
                                         key=lambda c: c[1]))
ALL_LANGUAGE_CHOICES = list(sorted(_all_languages_map.items(),
                                   key=lambda c: c[1]))

# Rough language order.  Based on a query of completed subtitle languages around 2016
LANGUAGE_POPULARITY = [
    'en', 'es', 'fr', 'ja', 'pt-br', 'ru', 'it', 'de', 'en-gb', 'tr', 'zh-cn',
    'ko', 'ar', 'pl', 'pt', 'zh-tw', 'cs', 'el', 'es-mx', 'nl', 'he', 'ro',
    'en-us', 'vi', 'hu', 'bg', 'sv', 'id', 'sr', 'uk', 'th', 'da', 'sk', 'hr',
    'nb', 'fa', 'ka', 'hi', 'ca', 'es-ar', 'fr-ca', 'fi', 'et', 'ms', 'sq',
    'ta', 'lt', 'sl', 'my', 'lv', 'eo', 'mk', 'es-419', 'es-es', 'hy',
    'zh-hk', 'mn', 'meta-tw', 'eu', 'ur', 'fil', 'gl', 'bn', 'ab', 'az', 'af',
    'zh', 'ml', 'sr-latn', 'bs', 'ku', 'mr', 'sh', 'zh-hant', 'meta-geo',
    'en-ca', 'is', 'te', 'gu', 'swa', 'be', 'tl', 'nl-be', 'la', 'zul', 'jv',
    'aa', 'kk', 'es-ni', 'arq', 'kn', 'zh-sg', 'km', 'no', 'iw', 'nn', 'amh',
    'ht', 'ga', 'cy', 'mt', 'ase', 'zh-hans', 'ne', 'yi', 'meta-audio', 'uz',
    'si', 'srp', 'ia', 'pt-pt', 'rm', 'bo', 'ast', 'de-ch', 'aka', 'que',
    'vls', 'fr-be', 'ry', 'lo', 'pan', 'xho', 'som', 'ug', 'ay', 'tlh', 'efi',
    'hau', 'ky', 'kl', 'an', 'ltg', 'meta-wiki', 'rup', 'as', 'ik', 'oc',
    'mus', 'mlg', 'ceb', 'bnt', 'en-ie', 'de-at', 'fy-nl', 'prs', 'wol', 'lb',
    'mi', 'tk', 'lg', 'lin', 'aeb', 'sco', 'tt', 'tg', 'yor', 'fo', 'lld',
    'ee', 'ps', 'ibo', 'kw', 'dz', 'cku', 'br', 'av', 'ie', 'nya', 'ce', 'cr',
    'sgn', 'ber', 'or', 'fr-ch', 'dv', 'bi', 'sm', 'pap', 'bam', 'gd', 'pi',
    'tet', 'orm', 'lkt', 'nr', 'hup', 'tir', 'bh', 'ae', 'nv', 'gn', 'tw',
    'kar', 'zam', 'cho', 'co', 'hz', 'sd', 'am', 'fj', 'inh', 'ful', 'ksh',
    'mos', 'sc', 'ch', 'ba', 'mo', 'iro', 'pnb', 'sw', 'se', 'to', 'cu',
    'arc', 'hb', 'io', 've', 'ff', 'sa', 'iu', 'cnh', 'nan', 'szl', 'ln',
    'hsb', 'kik', 'dsb', 'su', 'ho', 'pam', 'sg', 'kj', 'yaq', 'kau', 'za',
    'luo', 'kin', 'ss', 'ng', 'li', 'haw', 'gsw', 'bug', 'nd', 'gv', 'ii',
    'toj', 'tsz', 'wa', 'tsn', 'sn', 'pa', 'mh', 'kon', 'ctu', 'tzo', 'na',
    'run', 'ti', 'hai', 'fy', 'got', 'cv', 'mnk', 'luy', 'hus', 'haz', 'mad',
    'wbl', 'vo', 'kv', 'din', 'hch', 'umb',
]

SUPPORTED_LANGUAGE_CODES_BY_POPULARITY = [
    code for code in LANGUAGE_POPULARITY
    if code in SUPPORTED_LANGUAGE_CODES
]
SUPPORTED_LANGUAGE_CODES_BY_POPULARITY.extend(
    SUPPORTED_LANGUAGE_CODES.difference(SUPPORTED_LANGUAGE_CODES_BY_POPULARITY)
)

def _only_supported_languages(language_codes):
    """Filter the given list of language codes to contain only codes we support."""

    # TODO: Figure out the codec issue here.
    return [code for code in language_codes if code in SUPPORTED_LANGUAGE_CODES]


_get_language_choices_cache = {}
def get_language_choices(with_empty=False, with_any=False, flat=False):
    """Get a list of language choices

    We display languages as "<native_name> [code]", where native
    name is the how native speakers of the language would write it.

    We use the babel library to lookup the native name, however not all of our
    languages are handled by babel.  As a fallback we use the translations
    from gettext.

    Args:
        language_code -- language we're rendering the page in
    """

    language_code = get_language()
    try:
        languages = _get_language_choices_cache[language_code]
    except KeyError:
        languages = calc_language_choices(language_code)
        _get_language_choices_cache[language_code] = languages

    # make a copy of languages before we alter it
    languages = list(languages)
    if flat:
        languages = languages[1][1]
    if with_any:
        languages.insert(0, ('', _('--- Any Language ---')))
    if with_empty:
        languages.insert(0, ('', '---------'))
    return languages

def calc_language_choices(language_code):
    """Do the work for get_language_choices() """
    languages = []
    translation_locale = lookup_babel_locale(language_code)
    def label(code):
        english_name = _supported_languages_map[code]
        translated_name = _(english_name)
        return u'{} [{}]'.format(translated_name, code)
    languages.append((_('Popular'), [
        (code, label(code)) for code in
        SUPPORTED_LANGUAGE_CODES_BY_POPULARITY[:25]
    ]))
    languages.append((_('All'), [
        (code, label(code)) for code in sorted(SUPPORTED_LANGUAGE_CODES)
    ]))
    return languages

def choice_sort_key(item):
    return collator.sort_key(item[1])

babel_locale_blacklist = set(['tw'])
def lookup_babel_locale(language_code):
    if language_code == 'tw':
        # babel parses the Twi language as Akan, but this doesn't work for us
        # because "aka" is also Akan and we need to use a unique Locale for
        # each language code.
        return None
    try:
        return babel.Locale.parse(language_code, '-')
    except (babel.UnknownLocaleError, ValueError):
        return None

def get_language_choices_as_dicts(with_empty=False):
    """Return a list of language code choices labeled appropriately."""
    return [
        {'code': code, 'name': name}
        for (code, name) in get_language_choices(with_empty)
    ]

def get_language_label(code):
    """Return the translated, human-readable label for the given language code."""
    lc = LanguageCode(code, 'internal')
    return u'%s' % _(lc.name())

def get_user_languages_from_request(request, readable=False, guess=True):
    """Return a list of our best guess at languages that request.user speaks."""
    languages = []

    if request.user.is_authenticated():
        languages = request.user.get_languages()

    if guess and not languages:
        languages = languages_from_request(request)

    if readable:
        return map(get_language_label, _only_supported_languages(languages))
    else:
        return _only_supported_languages(languages)

def set_user_languages_to_cookie(response, languages):
    max_age = 60*60*24
    response.set_cookie(
        settings.USER_LANGUAGES_COOKIE_NAME,
        json.dumps(languages),
        max_age=max_age,
        expires=cookie_date(time.time() + max_age))

def get_user_languages_from_cookie(request):
    try:
        langs = json.loads(request.COOKIES.get(settings.USER_LANGUAGES_COOKIE_NAME, '[]'))
        return _only_supported_languages(langs)
    except (TypeError, ValueError):
        return []


def languages_from_request(request):
    languages = []

    for l in get_user_languages_from_cookie(request):
        if not l in languages:
            languages.append(l)

    if not languages:
        trans_lang = get_language()
        if not trans_lang in languages:
            languages.append(trans_lang)

        if hasattr(request, 'session'):
            lang_code = request.session.get('django_language', None)
            if lang_code is not None and not lang_code in languages:
                languages.append(lang_code)

        cookie_lang_code = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if cookie_lang_code and not cookie_lang_code in languages:
            languages.append(cookie_lang_code)

        accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        for lang, val in parse_accept_lang_header(accept):
            if lang and lang != '*' and not lang in languages:
                languages.append(lang)

    return _only_supported_languages(languages)

def languages_with_labels(langs):
    """Return a dict of language codes to language labels for the given seq of codes.

    These codes must be in the internal unisubs format.

    The labels will be in the standard label format.

    """
    return dict([code, get_language_label(code)] for code in langs)

# This handles RTL info for languages where get_language_info() is not correct
_RTL_OVERRIDE_MAP = {
    # there are languages on our system that are not on django.
    'arq': True,
    'pnb': True,
    # Forcing Azerbaijani to be a left-to-right language.
    # For: https://unisubs.sifterapp.com/projects/12298/issues/753035/comments 
    'az': False,
    # Force Urdu to be RTL (see gh-722)
    'ur': True,
    # Force Uyghur to be RTL (see gh-1411)
    'ug': True,
    # Force Aramaic to be RTL (gh-1073)
    'arc': True,
}

def is_rtl(language_code):
    if language_code in _RTL_OVERRIDE_MAP:
        return _RTL_OVERRIDE_MAP[language_code]
    try:
        return get_language_info(language_code)['bidi']
    except KeyError:
        return False
