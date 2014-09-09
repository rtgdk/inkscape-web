
from django.contrib.admin import ModelAdmin, StackedInline, site

from .forms import TemplateForm
from .models import *

class InlineTemplateAdmin(ModelAdmin):
    form = TemplateForm

site.register(InlineTemplate, InlineTemplateAdmin)

