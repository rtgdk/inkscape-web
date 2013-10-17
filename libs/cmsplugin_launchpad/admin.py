
from django.contrib import admin
from cmsplugin_launchpad.models import Project, BugCount

class ProjectAdmin(admin.ModelAdmin):
    model = Project
    date_hierarchy = 'updated'
    exclude = ('updated',)

class BugCountAdmin(admin.ModelAdmin):
    model = BugCount
    date_hierarchy = 'updated'
    exclude = ('bugs',)

admin.site.register(Project, ProjectAdmin)
admin.site.register(BugCount, BugCountAdmin)

