from django.db import models
from django.utils.functional import Promise
from django.utils.encoding import force_unicode
from types import ClassType, TypeType
import base64
import uuid
try:
    import cPickle as pickle
except ImportError:
    import pickle


def has_sentry_metadata(value):
    try:
        return callable(getattr(value, '__sentry__', None))
    except:
        return False


def to_unicode(value):
    try:
        value = unicode(force_unicode(value))
    except (UnicodeEncodeError, UnicodeDecodeError):
        value = '(Error decoding value)'
    except Exception: # in some cases we get a different exception
        try:
            value = str(repr(type(value)))
        except Exception:
            value = '(Error decoding value)'
    return value


def transform(value, stack=[], context=None):
    # TODO: make this extendable
    # TODO: include some sane defaults, like UUID
    # TODO: dont coerce strings to unicode, leave them as strings
    if context is None:
        context = {}
    objid = id(value)
    if objid in context:
        return '<...>'
    context[objid] = 1
    if any(value is s for s in stack):
        ret = 'cycle'
    transform_rec = lambda o: transform(o, stack + [value], context)
    if isinstance(value, (tuple, list, set, frozenset)):
        ret = type(value)(transform_rec(o) for o in value)
    elif isinstance(value, uuid.UUID):
        ret = repr(value)
    elif isinstance(value, dict):
        ret = dict((k, transform_rec(v)) for k, v in value.iteritems())
    elif isinstance(value, unicode):
        ret = to_unicode(value)
    elif isinstance(value, str):
        try:
            ret = str(value)
        except:
            ret = to_unicode(value)
    elif not isinstance(value, (ClassType, TypeType)) and \
            has_sentry_metadata(value):
        ret = transform_rec(value.__sentry__())
    elif isinstance(value, Promise):
        # EPIC HACK
        pre = value.__class__.__name__[1:]
        value = getattr(value, '%s__func' % pre)(*getattr(value, '%s__args' % pre), **getattr(value, '%s__kw' % pre))
        return transform(value)
    elif not isinstance(value, (int, bool)) and value is not None:
        try:
            ret = transform(repr(value))
        except:
            # It's common case that a model's __unicode__ definition may try to query the database
            # which if it was not cleaned up correctly, would hit a transaction aborted exception
            ret = u'<BadRepr: %s>' % type(value)
    else:
        ret = value
    del context[objid]
    return ret


class GzippedDictField(models.TextField):
    """
    Slightly different from a JSONField in the sense that the default
    value is a dictionary.
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, basestring) and value:
            value = pickle.loads(base64.b64decode(value).decode('zlib'))
        elif not value:
            return {}
        return value

    def get_prep_value(self, value):
        if value is None: return
        return base64.b64encode(pickle.dumps(transform(value)).encode('zlib'))

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.TextField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)


class WidgetDialogLog(models.Model):
    date_saved = models.DateTimeField(auto_now_add=True)
    browser_id = models.CharField(max_length=127)
    log = models.TextField()

class WidgetDialogCall(models.Model):
    date_saved = models.DateTimeField(auto_now_add=True)
    browser_id = models.CharField(max_length=127)
    method = models.CharField(max_length=127)
    request_args = GzippedDictField()
