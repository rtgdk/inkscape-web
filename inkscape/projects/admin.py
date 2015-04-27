
from django.contrib.admin import *
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin

from .models import *

class WorkerInline(TabularInline):
    model = Worker
    extra = 0

class DeliverableInline(TabularInline):
    model = Deliverable

class UpdateInline(StackedInline):
    model = ProjectUpdate
    extra = 1
    readonly_fields = ('creator',)

class ProjectAdmin(AjaxSelectAdmin):
    list_display = ('title', 'manager', 'started')
    form  = make_ajax_form(Project, {
      'manager': 'user',
      'reviewer': 'user',
      'second': 'user' })
    
    fieldsets = (
        (None, {
          'fields': ('title', 'project_type', 'banner', 'logo', 'is_fundable', 'is_approved', 'sort')
        }),
        ('Timing', {
          'classes': ('collapse',),
          'fields': ('duration', 'started', 'finished'),
        }),
        ('People', {
          'classes': ('collapse',),
          'fields': ('proposer', 'manager', 'reviewer', 'second')
        }),
        ('Criteria', {
          'fields': ('criteria',),
        }),
        ('Static Information', {
          'classes': ('collapse',),
          'fields': ('slug', 'created', 'edited'),
        }),
    )
    readonly_fields = ('proposer','slug','created','edited')
    filter_horizontal = ("criteria",)
    inlines = (DeliverableInline, UpdateInline, WorkerInline)

site.register(Project, ProjectAdmin)
site.register(ProjectType)
site.register(Criteria)

class TaskInline(TabularInline):
    model = Task
    extra = 3

class DeliverableAdmin(ModelAdmin):
    list_display = ('name', 'project', 'finished')
    inlines = (TaskInline,)

site.register(Deliverable, DeliverableAdmin)

