from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext
from django.contrib import admin

from inkscape.tracker.models import Bug, Tag, Blueprint

class BugsAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ('title', 'status', 'level', 'owner')
    list_filter = ('status', 'level', 'tags')
    search_fields = ['title', 'tags']

class TagsAdmin(admin.ModelAdmin):
    list_display = ('name',)

#class BlueprintAdmin(admin.ModelAdmin):
#    date_hierarchy = 'created'
#    list_display = ('title', 'status', 'level', 'owner')
#    list_filter = ('status', 'level', 'tags')
#    search_fields = ['title', 'tags']
#    form = NewsForm

admin.site.register(Bug, BugsAdmin)
admin.site.register(Tag, TagsAdmin)
#admin.site.register(Blueprint, BlueprintAdmin)
