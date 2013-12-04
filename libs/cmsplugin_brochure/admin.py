
from django.contrib import admin
from cmsplugin_brochure.models import Brochure

class BrochureAdmin(admin.ModelAdmin):
    date_hierarchy = 'publish'
    list_display = ('name', 'publish')
    actions = ['_refresh']

    def _refresh(self, request, queryset):
        for item in queryset:
            item.refresh()

    _refresh.short_description = 'Refresh Feed Now'


admin.site.register(Brochure, BrochureAdmin)

