
from django.contrib.admin import ModelAdmin, StackedInline, site

from .models import *

class ProjectAdmin(ModelAdmin):
    readonly_fields = ('slug',)
    list_display = ('title', 'manager', 'started')

site.register(Project, ProjectAdmin)
site.register(ProjectType)

