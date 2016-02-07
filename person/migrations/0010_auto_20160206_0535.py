# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0009_auto_20160206_0435'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': [('use_irc', 'IRC Chat Training Complete'), ('website_cla_agreed', 'Agree to Website License')]},
        ),
        migrations.AlterField(
            model_name='team',
            name='icon',
            field=models.ImageField(default=b'/static/images/team.svg', upload_to=b'teams', verbose_name='Display Icon'),
        ),
    ]
