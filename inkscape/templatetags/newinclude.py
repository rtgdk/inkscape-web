"""
This is ripped from trunk as it's come in since 1.2 but I can't work with a 1.3
dependency. But still I need {% include 'foo' with bar='baz' %} so I've renamed
it to newinclude.

http://code.djangoproject.com/browser/django/trunk/django/template/\
loader_tags.py?rev=15413

http://code.djangoproject.com/browser/django/trunk/django/template/\
defaulttags.py?rev=14922
"""
from django.template import TemplateSyntaxError
from django.template import Library, Node
from django.template.context import Context
from django.template.loader import get_template
from django.conf import settings

register = Library()

import re

# Regex for token keyword arguments
kwarg_re = re.compile(r"(?:(\w+)=)?(.+)")

def token_kwargs(bits, parser, support_legacy=False):
    """
    A utility method for parsing token keyword arguments.

    :param bits: A list containing remainder of the token (split by spaces)
        that is to be checked for arguments. Valid arguments will be removed
        from this list.

    :param support_legacy: If set to true ``True``, the legacy format
        ``1 as foo`` will be accepted. Otherwise, only the standard ``foo=1``
        format is allowed.

    :returns: A dictionary of the arguments retrieved from the ``bits`` token
        list.

    There is no requirement for all remaining token ``bits`` to be keyword
    arguments, so the dictionary will be returned as soon as an invalid
    argument format is reached.
    """
    if not bits:
        return {}
    match = kwarg_re.match(bits[0])
    kwarg_format = match and match.group(1)
    if not kwarg_format:
        if not support_legacy:
            return {}
        if len(bits) < 3 or bits[1] != 'as':
            return {}

    kwargs = {}
    while bits:
        if kwarg_format: 
            match = kwarg_re.match(bits[0])
            if not match or not match.group(1):
                return kwargs
            key, value = match.groups()
            del bits[:1]
        else:
            if len(bits) < 3 or bits[1] != 'as':
                return kwargs
            key, value = bits[2], bits[0]
            del bits[:3]
        kwargs[key] = parser.compile_filter(value)
        if bits and not kwarg_format:
            if bits[0] != 'and':
                return kwargs
            del bits[:1]
    return kwargs

class BaseIncludeNode(Node):
    def __init__(self, *args, **kwargs):
        self.extra_context = kwargs.pop('extra_context', {})
        self.isolated_context = kwargs.pop('isolated_context', False)
        super(BaseIncludeNode, self).__init__(*args, **kwargs)

    def render_template(self, template, context):
        values = dict([(name, var.resolve(context)) for name, var
                       in self.extra_context.iteritems()])
        if self.isolated_context:
            return template.render(Context(values))
        context.update(values)
        output = template.render(context)
        context.pop()
        return output

class ConstantIncludeNode(BaseIncludeNode):
    def __init__(self, template_path, *args, **kwargs):
        super(ConstantIncludeNode, self).__init__(*args, **kwargs)
        try:
            t = get_template(template_path)
            self.template = t
        except:
            if settings.TEMPLATE_DEBUG:
                raise
            self.template = None

    def render(self, context):
        if not self.template:
            return ''
        return self.render_template(self.template, context)

class IncludeNode(BaseIncludeNode):
    def __init__(self, template_name, *args, **kwargs):
        super(IncludeNode, self).__init__(*args, **kwargs)
        self.template_name = template_name

    def render(self, context):
        try:
            template_name = self.template_name.resolve(context)
            template = get_template(template_name)
            return self.render_template(template, context)
        except:
            if settings.TEMPLATE_DEBUG:
                raise
            return ''

def do_include(parser, token):
    """
    Loads a template and renders it with the current context. You can pass
    additional context using keyword arguments.

    Example::

        {% include "foo/some_include" %}
        {% include "foo/some_include" with bar="BAZZ!" baz="BING!" %}

    Use the ``only`` argument to exclude the current context when rendering
    the included template::

        {% include "foo/some_include" only %}
        {% include "foo/some_include" with bar="1" only %}
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("%r tag takes at least one argument: the name of the template to be included." % bits[0])
    options = {}
    remaining_bits = bits[2:]
    while remaining_bits:
        option = remaining_bits.pop(0)
        if option in options:
            raise TemplateSyntaxError('The %r option was specified more '
                                      'than once.' % option)
        if option == 'with':
            value = token_kwargs(remaining_bits, parser, support_legacy=False)
            if not value:
                raise TemplateSyntaxError('"with" in %r tag needs at least '
                                          'one keyword argument.' % bits[0])
        elif option == 'only':
            value = True
        else:
            raise TemplateSyntaxError('Unknown argument for %r tag: %r.' %
                                      (bits[0], option))
        options[option] = value
    isolated_context = options.get('only', False)
    namemap = options.get('with', {})
    path = bits[1]
    if path[0] in ('"', "'") and path[-1] == path[0]:
        return ConstantIncludeNode(path[1:-1], extra_context=namemap,
                                   isolated_context=isolated_context)
    return IncludeNode(parser.compile_filter(bits[1]), extra_context=namemap,
                       isolated_context=isolated_context)

register.tag('newinclude', do_include)
