
from django.template.base import Library
from django.conf import settings

from cms.models.pagemodel import Page

register = Library()

@register.inclusion_tag('cms/plugins/toc_branch.html')
def toc_branch(toc, bullet=False):
    return {'children': toc, 'bullet': bullet}


