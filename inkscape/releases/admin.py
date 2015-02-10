
from django.contrib.admin import *

from .models import *

class PlatformInline(StackedInline):
    model = ReleasePlatform
    extra = 1
    #readonly_fields = ('created',)
    #list_display = ('title', 'manager', 'started')

class ReleaseAdmin(ModelAdmin):
    inlines = (PlatformInline,)

site.register(Release, ReleaseAdmin)
site.register(Platform)
site.register(ReleasePlatform)

