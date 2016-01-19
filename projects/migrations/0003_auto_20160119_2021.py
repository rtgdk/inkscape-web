# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pile.fields


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_auto_20160119_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='banner',
            field=pile.fields.ResizedImageField(format=b'PNG', default=b'/static/images/project_banner.png', upload_to=b'project/banner', max_width=920, min_height=90, max_height=120, min_width=600, verbose_name='Banner (920x120)'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='logo',
            field=pile.fields.ResizedImageField(format=b'PNG', default=b'/static/images/project_logo.png', upload_to=b'project/logo', max_width=150, min_height=150, max_height=150, min_width=150, verbose_name='Logo (150x150)'),
            preserve_default=True,
        ),
    ]
