"inkscape_i18n template tags"

from django import template
from django.conf import settings
from .. import langurl

register = template.Library()


@register.tag('langurl')
def langurl_tag(parser, token):
    """
    Get a link to the current page or another page in a different language.

    * ``{% langurl 'de' %}`` gives the URL to the current page in German.
    * ``{% langurl 'de' '/about/' %}`` gives the URL to ``/about/`` in German.
    """

    tokens = token.split_contents()
    if len(tokens) == 2:
        return LangURLNode(tokens[1])
    elif len(tokens) == 3:
        return LangURLNode(tokens[1], tokens[2])
    else:
        raise template.TemplateSyntaxError(
                "%r tag requires one or two arguments" % tokens[0])


class LangURLNode(template.Node):
    def __init__(self, subdomain, path=None):
        self.subdomain = template.Variable(subdomain)
        self.path = path if path is None else template.Variable(path)

    def render(self, context):
        request = context['request']  # requires RequestMiddleware
        subdomain = self.subdomain.resolve(context)
        return langurl(subdomain,
                self.path is None and request or self.path.resolve(context))
