# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import pile.fields


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0008_auto_20160527_0115'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReleaseStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('desc', models.CharField(max_length=128, verbose_name='Description')),
                ('style', models.CharField(blank=True, max_length=32, null=True, choices=[(b'blue', 'Blue')])),
                ('icon', pile.fields.ResizedImageField(format=b'PNG', upload_to=b'release/icons', max_width=32, min_height=0, max_height=32, blank=True, min_width=0, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='release',
            name='status',
            field=models.ForeignKey(blank=True, to='releases.ReleaseStatus', null=True),
        ),
    ]
