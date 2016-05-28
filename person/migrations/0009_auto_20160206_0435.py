# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0008_auto_20160204_0335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='icon',
            field=models.ImageField(default=b'https://inkscape.global.ssl.fastly.net/static/images/team.svg', upload_to=b'teams', verbose_name='Display Icon'),
        ),
    ]
