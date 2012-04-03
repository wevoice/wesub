from django.forms.widgets import Textarea
from livesettings.values import LongStringValue, NOTSET

from utils.forms import EmailListField


class EmailListValue(LongStringValue):
    class field(EmailListField):
        def __init__(self, *args, **kwargs):
            kwargs['required'] = False
            kwargs['widget'] = Textarea()
            EmailListField.__init__(self, *args, **kwargs)

    def to_python(self, value):
        if value == NOTSET:
            value = []

        if isinstance(value, (list, tuple)):
            return value

        return value.split(',')

    def get_db_prep_save(self, value):
        if value == NOTSET:
            value = []

        return ','.join(value)

    def to_editor(self, value):
        if value == NOTSET:
            value = []

        if isinstance(value, (list, tuple)):
            return ','.join(value)

        return value


