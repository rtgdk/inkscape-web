# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LogFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inode', models.PositiveIntegerField(unique=True, db_index=True)),
                ('touched', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='LogMetric',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(unique=True, max_length=32)),
                ('unit', models.CharField(max_length=8, null=True, blank=True)),
                ('label', models.CharField(max_length=32)),
                ('has_family', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='LogName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('family', models.CharField(max_length=128, null=True, db_index=True)),
                ('re_name', models.CharField(help_text=b'Rename this metric value to something else.', max_length=255, db_index=True)),
                ('re_family', models.CharField(help_text=b'Rename this family to something else.', max_length=255, null=True, db_index=True, blank=True)),
            ],
            options={
                'ordering': ['name', 'family'],
            },
        ),
        migrations.CreateModel(
            name='LogPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(db_index=True)),
                ('period', models.IntegerField(default=0, choices=[(0, b'Day'), (1, b'Week Day'), (2, b'Week of Year'), (3, b'Month'), (4, b'Year')])),
            ],
            options={
                'ordering': ['period', 'date', 'request'],
            },
        ),
        migrations.CreateModel(
            name='LogRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=255, unique=True, null=True, db_index=True)),
            ],
            options={
                'ordering': ['path'],
            },
        ),
        migrations.CreateModel(
            name='LogValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.PositiveIntegerField(default=0)),
                ('high', models.PositiveIntegerField(null=True)),
                ('low', models.PositiveIntegerField(null=True)),
                ('avg', models.PositiveIntegerField(null=True)),
                ('metric', models.ForeignKey(related_name='values', to='logbook.LogMetric')),
                ('name', models.ForeignKey(related_name='values', to='logbook.LogName', null=True)),
                ('period', models.ForeignKey(related_name='values', to='logbook.LogPeriod')),
            ],
            options={
                'ordering': ['metric', 'period', 'name'],
            },
        ),
        migrations.AddField(
            model_name='logperiod',
            name='request',
            field=models.ForeignKey(related_name='periods', to='logbook.LogRequest'),
        ),
        migrations.AlterUniqueTogether(
            name='logname',
            unique_together=set([('name', 'family')]),
        ),
        migrations.AlterUniqueTogether(
            name='logvalue',
            unique_together=set([('metric', 'period', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='logperiod',
            unique_together=set([('period', 'date', 'request')]),
        ),
    ]
