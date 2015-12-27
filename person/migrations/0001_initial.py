# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pile.fields
from django.conf import settings
import django.core.validators

class FakeCreateModel(migrations.CreateModel):
    def database_forwards(self, *args, **kwargs):
        pass
    def database_backwards(self, *args, **kwargs):
        pass

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'auth_user',
                'permissions': [('website_cla_agreed', 'Agree to Website License')],
            },
        ),
        migrations.CreateModel(
            name='Ballot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('desc', models.TextField(blank=True, null=True, verbose_name='Full Description', validators=[django.core.validators.MaxLengthValidator(10240)])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BallotItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('ballot', models.ForeignKey(related_name='items', to='person.Ballot')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BallotVotes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=0)),
                ('ballot', models.ForeignKey(related_name='votes', to='person.Ballot')),
                ('item', models.ForeignKey(related_name='votes', to='person.BallotItem')),
                ('user', models.ForeignKey(related_name='ballot_votes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='User Team')),
                ('slug', models.SlugField(max_length=32, verbose_name='Group ID')),
                ('icon', models.ImageField(upload_to=b'teams', verbose_name='Display Icon')),
                ('intro', models.TextField(blank=True, null=True, verbose_name='Introduction', validators=[django.core.validators.MaxLengthValidator(1024)])),
                ('desc', models.TextField(blank=True, null=True, verbose_name='Full Description', validators=[django.core.validators.MaxLengthValidator(10240)])),
                ('mailman', models.CharField(max_length=256, null=True, verbose_name='Mailing List', blank=True)),
                ('enrole', models.CharField(default=b'O', max_length=1, verbose_name='Open Enrolement', choices=[(b'O', 'Open'), (b'P', 'Peer Invite'), (b'T', 'Admin Invite'), (b'C', 'Closed'), (b'S', 'Secret')])),
                ('admin', models.ForeignKey(related_name='teams', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('members', pile.fields.AutoOneToOneField(related_name='team', null=True, blank=True, to='auth.Group')),
                ('watchers', models.ManyToManyField(related_name='watches', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bio', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(4096)])),
                ('photo', pile.fields.ResizedImageField(format=b'PNG', upload_to=b'photos', max_width=190, min_height=0, max_height=190, blank=True, min_width=0, null=True, verbose_name='Photograph (square)')),
                ('ircnick', models.CharField(max_length=20, null=True, verbose_name='IRC Nickname', blank=True)),
                ('ircpass', models.CharField(max_length=128, null=True, verbose_name='Freenode Password (optional)', blank=True)),
                ('ircdev', models.BooleanField(default=False, verbose_name='Join Developer Channel')),
                ('dauser', models.CharField(max_length=64, null=True, verbose_name='deviantArt User', blank=True)),
                ('ocuser', models.CharField(max_length=64, null=True, verbose_name='openClipArt User', blank=True)),
                ('tbruser', models.CharField(max_length=64, null=True, verbose_name='Tumblr User', blank=True)),
                ('gpg_key', models.TextField(blank=True, null=True, verbose_name='GPG Public Key', validators=[django.core.validators.MaxLengthValidator(262144)])),
                ('last_seen', models.DateTimeField(null=True, blank=True)),
                ('visits', models.IntegerField(default=0)),
                ('user', pile.fields.AutoOneToOneField(related_name='details', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='ballotvotes',
            unique_together=set([('user', 'item', 'order')]),
        ),
        migrations.AddField(
            model_name='ballot',
            name='team',
            field=models.ForeignKey(related_name='ballots', to='person.Team'),
            preserve_default=True,
        ),
    ]
