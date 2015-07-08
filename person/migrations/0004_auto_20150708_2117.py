# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0003_auto_20150606_0226'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userdetails',
            options={'permissions': [('website_cla_agreed', 'Agree to Website License')]},
        ),
    ]
