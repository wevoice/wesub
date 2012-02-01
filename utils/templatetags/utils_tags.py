import urlparse
from django import template
from django.utils.translation import ugettext
from django.contrib.sites.models import Site
from django.template.defaulttags import URLNode, url
from django.template.defaultfilters import linebreaksbr
from django.template.defaultfilters import stringfilter
from django.utils.html import escape
from utils.translation import SUPPORTED_LANGUAGES_DICT_LAZY
from pprint import pformat

try:
    from django.utils.safestring import mark_safe
except ImportError: # v0.96 and 0.97-pre-autoescaping compat
    def mark_safe(x): return x

register = template.Library()

@register.simple_tag
def form_field_as_list(GET_vars, bounded_field, count=0):
    getvars = '?'
    
    if len(GET_vars.keys()) > 0:
        getvars = "?%s&" % GET_vars.urlencode()
    
    output = []
    
    data = bounded_field.data or bounded_field.field.initial

    for i, choice in enumerate(bounded_field.field.choices):
        if choice[0] == data:
            li_attrs = u'class="active"'
        else:
            li_attrs = u''
        
        href = u'%s%s=%s' % (getvars, bounded_field.name, choice[0])
        li = {
            'attrs': li_attrs,
            'href': href,
            'value': choice[0],
            'fname': bounded_field.html_name,
            'name': choice[1]
        }
        
        if count and choice[0] == data and i >= count:
            output.insert(count - 1, li)
        else:
            output.append(li)

    if count:
        li = {
            'attrs': u'class="more-link"',
            'href': '#',
            'name': ugettext(u'more...'),
            'fname': '',
            'value': ''
        }        
        output.insert(count, li)
        
        for i in xrange(len(output[count+1:])):
            output[count+i+1]['attrs'] += u' style="display: none"'

    content = [u'<ul>']
    for item in output:
        content.append(u'<li %(attrs)s><a href="%(href)s" name="%(fname)s" value="%(value)s"><span>%(name)s</span></a></li>' % item) 
    content.append(u'</ul>')
    
    return u''.join(content)



def parse_tokens(parser, bits):
    """
    Parse a tag bits (split tokens) and return a list on kwargs (from bits of the  fu=bar) and a list of arguments.
    """

    kwargs = {}
    args = []
    for bit in bits[1:]:
        try:
            try:
                pair = bit.split('=')
                kwargs[str(pair[0])] = parser.compile_filter(pair[1])
            except IndexError:
                args.append(parser.compile_filter(bit))
        except TypeError:
            raise template.TemplateSyntaxError('Bad argument "%s" for tag "%s"' % (bit, bits[0]))

    return args, kwargs

class ZipLongestNode(template.Node):
    """
    Zip multiple lists into one using the longest to determine the size

    Usage: {% zip_longest list1 list2 <list3...> as items %}
    """
    def __init__(self, *args, **kwargs):
        self.lists = args
        self.varname = kwargs['varname']

    def render(self, context):
        lists = [e.resolve(context) for e in self.lists]

        if self.varname is not None:
            context[self.varname] = [i for i in map(lambda *a: a, *lists)]
        return ''

@register.tag
def zip_longest(parser, token):
    bits = token.contents.split()
    varname = None
    if bits[-2] == 'as':
        varname = bits[-1]
        del bits[-2:]
    else:
        # raise exception
        pass
    args, kwargs = parse_tokens(parser, bits)

    if varname:
        kwargs['varname'] = varname

    return ZipLongestNode(*args, **kwargs)

# from http://djangosnippets.org/snippets/1518/
# watchout, if you change the site domain this value will get stale
domain = "http://%s" % Site.objects.get_current().domain

class AbsoluteURLNode(URLNode):
    def render(self, context):
        if self.asvar:  
            context[self.asvar]= urlparse.urljoin(domain, context[self.asvar])  
            return ''  
        else:  
            return urlparse.urljoin(domain, path)
        path = super(AbsoluteURLNode, self).render(context)
        domain = "http://%s" % Site.objects.get_current().domain
        return urlparse.urljoin(domain, path)

def absurl(parser, token, node_cls=AbsoluteURLNode):
    """Just like {% url %} but ads the domain of the current site."""
    node_instance = url(parser, token)
    return node_cls(view_name=node_instance.view_name,
        args=node_instance.args,
        kwargs=node_instance.kwargs,
        asvar=node_instance.asvar)
absurl = register.tag(absurl)

@register.filter
@stringfilter
def lang_name_from_code(value):
    return SUPPORTED_LANGUAGES_DICT_LAZY.get(value, value)

@register.filter
def rawdump(x):
    if hasattr(x, '__dict__'):
        d = {
            '__str__':str(x),
            '__unicode__':unicode(x),
            '__repr__':repr(x),
            'dir':dir(x),
        }
        d.update(x.__dict__)
        x = d
    output = pformat(x)+'\n'
    return output

DUMP_TEMPLATE = '<pre class="dump"><code class="python" style="font-family: Menlo, monospace; white-space: pre;">%s</code></pre>'
@register.filter
def dump(x):
    return mark_safe(DUMP_TEMPLATE % escape(rawdump(x)))

@register.filter
def simplify_number(value):
    num = str(value)
    size = len(num)

    # Billions
    if size > 9:
        bils = num[0:-9]
        dec = num[-9:-8]
        if dec != '0':
            return '{0}.{1}b'.format(bils, dec)
        else:
            return '{0}b'.format(bils)

    # Millions
    elif size > 6:
        mils = num[0:-6]
        dec = num[-6:-5]
        if dec != '0':
            return '{0}.{1}m'.format(mils, dec)
        else:
            return '{0}m'.format(mils)

    # Ten-thousands
    elif size > 4:
        thou = num[0:-3]
        dec = num[-3:-2]
        if dec != '0':
            return '{0}.{1}k'.format(thou, dec)
        else:
            return '{0}k'.format(thou)

    else:
        return num