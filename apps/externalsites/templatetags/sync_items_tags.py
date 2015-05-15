import json
from django.template.defaulttags import register
@register.filter
def get_fields(dictionary):
    return json.loads(dictionary)
