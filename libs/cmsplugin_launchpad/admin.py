
from django.contrib import admin
from cmsplugin_launchpad.models import Project, BugCount,\
        BugStatus, BugImportance


class LpAdmin(admin.ModelAdmin):
    date_hierarchy = 'updated'
    list_display = ('name', 'updated')
    actions = ['_refresh']

    def _refresh(self, request, queryset):
        for item in queryset:
            item.refresh()

    _refresh.short_description = 'Refresh from Launchpad'

class ProjectAdmin(LpAdmin):
    model = Project
    date_hierarchy = 'updated'
    list_display = ('name', 'focus', 'updated')
    exclude = ('focus',)

class BugCountAdmin(LpAdmin):
    model = BugCount
    list_display = ('name', 'bugs', 'updated')
    exclude = ('bugs',)

admin.site.register(Project, ProjectAdmin)
admin.site.register(BugCount, BugCountAdmin)
admin.site.register(BugStatus)
admin.site.register(BugImportance)

