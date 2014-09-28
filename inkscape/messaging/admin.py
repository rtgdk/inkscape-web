
from django.contrib.admin import ModelAdmin, StackedInline, site

from .models import *

site.register(AlertType)
site.register(UserAlert)
site.register(UserAlertSetting)

site.register(Message)

