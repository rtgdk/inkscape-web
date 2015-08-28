# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import pile.fields


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0005_auto_20150825_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='admin',
            field=models.ForeignKey(related_name='admin_teams', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='team',
            name='group',
            field=pile.fields.AutoOneToOneField(related_name='team', default=1, to='auth.Group'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='team',
            name='icon',
            field=models.ImageField(default=b'/static/images/team.svg', upload_to=b'teams', verbose_name='Display Icon'),
            preserve_default=True,
        ),
    ]
