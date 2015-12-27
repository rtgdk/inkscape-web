# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

FIELDS = ['user', 'bio', 'photo', 'language', 'ircnick', 'ircpass', 'ircdev',
          'dauser', 'ocuser', 'tbruser', 'gpg_key', 'last_seen', 'visits']

def migrate_userdetails(apps, schema_editor):
    User = apps.get_model("person", "User")
    for user in User.objects.all():
        for field in FIELDS:
            try:
                setattr(user, field, getattr(user.details, field, None))
            except Exception:
                pass
        user.save()

def backwards_userdetails(apps, schema_editor):
    User = apps.get_model("person", "User")
    for user in User.objects.all():
        for field in FIELDS:
            try:
                setattr(user.details, field, getattr(user, field, None))
            except Exception:
                pass
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0010_auto_20151227_0221'),
    ]

    operations = [
        migrations.RunPython(migrate_userdetails, backwards_userdetails),
    ]
