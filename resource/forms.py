#
# Copyright 2013, Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Forms for the gallery system
"""
from django.forms import *
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.db.models import Model, Q
from django.utils.timezone import now

from .models import *
from .utils import ALL_TEXT_TYPES

# Thread-safe current user middleware getter.
from cms.utils.permissions import get_current_user as get_user

from django.core.files.uploadedfile import InMemoryUploadedFile
from cStringIO import StringIO

__all__ = ('FORMS', 'GalleryForm', 'MoveForm', 'ResourceFileForm', 'ResourcePasteForm', 'ResourceAddForm', 'MirrorAddForm')

class GalleryForm(ModelForm):
    class Meta:
        model = Gallery
        fields = ['name','group']

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        self.fields['group'].queryset = get_user().groups.all()


class MoveForm(ModelForm):
    target = ChoiceField()

    class Meta:
        model = Resource
        fields = ['target']

    def get_galleries(self):
        return [ (item.pk, str(item)) for item in Gallery.objects.filter(
            (Q(user=self.instance.user) & Q(group__isnull=True))
            | Q(group__in=self.instance.user.groups.all())
        )]

    def __init__(self, *args, **kwargs):
        super(MoveForm, self).__init__(*args, **kwargs)
        self.fields['target'].choices = self.get_galleries()

    def save(self):
        # XXX here


class ResourceBaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        if hasattr(self.Meta, 'required'):
            for key in self.Meta.required:
                self.fields[key].required = True

        self.user = get_user()
        if not self.user.is_authenticated():
            raise ValueError("Anonymous user can't create or edit resources!")

        if not self.user.has_perm('resource.change_resourcemirror'):
            self.fields.pop('mirror', None)
        if not self.user.details.gpg_key:
            self.fields.pop('signature', None)
        if not self.instance or self.instance.mime().is_image():
            self.fields.pop('thumbnail', None)

        for field in ('download', 'thumbnail', 'signature'):
            if field in self.fields and self.fields[field].widget is ClearableFileInput:
                self.fields[field].widget = FileInput()

        if 'category' in self.fields:
            f = self.fields['category']
            f.queryset = f.queryset.filter(visible=True).filter(
                Q(start_contest__isnull=True) | (
                Q(start_contest__lt=now().date()) &
                Q(end_contest__gt=now().date()) ))

        if 'owner' in self.fields:
            f = self.fields['owner']
            f.to_python = self.ex_clean_owner(f.to_python)
        
    def ex_clean_owner(self, f):
        """We want to clean owner, but django to_python validator catches our
           error before we get a chance to explain it to the user. Intercept in
           this crazy way."""
        def _internal(val):
            if val in (None, u'None'):
                raise ValidationError(_("You need to have permission to post this work, or be the owner of the work."))
            return f(val)
        return _internal

    def clean_license(self):
        """Make sure the category accepts this kind of license"""
        ret = self.cleaned_data['license']
        if 'category' in self._meta.fields:
            category = self.cleaned_data.get('category', None)
            if category and ret not in category.acceptable_licenses.all():
                raise ValidationError(_("This is not an acceptable license for this category"))
        return ret

    def clean_category(self):
        """Make sure the category voting rules are followed"""
        ret = self.cleaned_data['category']
        obj = self.instance
        if (not obj or obj.category != ret) and ret.start_contest:
            if obj.votes.all().count() > 0:
                raise ValidationError(_("You can not assign an item with existing votes to a contest."))
        return ret

    def clean_mirror(self):
        """Update the edited time/date if mirror flag changed"""
        ret = self.cleaned_data['mirror']
        if self.instance and ret != self.instance.mirror:
            self.instance.edited = now()
        return ret

    def clean_download(self):
        download = self.cleaned_data['download']
        # Don't check the size of existing uploads or not-saved items
        if self.instance and self.instance.download != download:
            space = (self.user.quota() * 1024) - self.user.resources.disk_usage()
            if download.size > space:
                raise ValidationError("Not enough space to upload this file.")
        return download

    def save(self, commit=False, **kwargs):
        obj = ModelForm.save(self, commit=False)
        if not obj.id:
            obj.user = self.user
        obj.save(**kwargs)
        return obj

    @property
    def auto(self):
        for field in list(self):
            if field.name in ['name', 'desc', 'download']:
                continue
            yield field


class ResourceFileForm(ResourceBaseForm):
    published = BooleanField(label=_('Publicly Visible'), required=False)

    class Meta:
        model = ResourceFile
        fields = ['name', 'desc', 'link', 'category', 'license', 'owner',
                  'thumbnail', 'signature', 'published', 'mirror', 'download']
        required = ['name', 'category', 'license', 'owner']



class ResourcePasteForm(ResourceBaseForm):
    media_type = ChoiceField(label=_('Text Format'), choices=ALL_TEXT_TYPES)
    download   = CharField(label=_('Pasted Text'), widget=Textarea, required=False)

    def __init__(self, data=None, *args, **kwargs):
        # These are shown items values, for default values see save()
        i = dict(
            download='', desc='-', license=1, media_type='text/plain',
            name=_("Pasted Text #%d") % ResourceFile.objects.all().count(),
        )
        i.update(kwargs.pop('initial', {}))
        kwargs['initial'] = i

        d = data and dict((key, data.get(key, i[key])) for key in i.keys())

        super(ResourcePasteForm, self).__init__(d, *args, **kwargs)

    def _clean_fields(self):
        for key in self.initial:
            self.cleaned_data.setdefault(self.initial[key])
        return super(ResourcePasteForm, self)._clean_fields()

    def clean_download(self):
        text = self.cleaned_data['download']
        # We don't call super clean_download because it would check the quota.
        # Text pastes are exempt from the quota system and are always allowed.
        if len(text) < 200:
            raise ValidationError("Text is too small for the pastebin.")

        filename = "pasted-%s.txt" % slugify(self.cleaned_data['name'])
        buf = StringIO(text.encode('utf-8'))
        buf.seek(0, 2)

        return InMemoryUploadedFile(buf, "text", filename, None, buf.tell(), None)

    def save(self, **kwargs):
        obj = super(ResourcePasteForm, self).save(**kwargs)
        if not obj.category and obj.id:
            obj.category = Category.objects.get(pk=1)
            obj.owner = True
            obj.published = True
            obj.save()
        return obj

    class Meta:
        model = ResourceFile
        fields = ['name', 'desc', 'media_type', 'license', 'link', 'download']
        required = ['name', 'license']


class ResourceEditPasteForm(ResourceBaseForm):
    media_type = ChoiceField(label=_('Text Format'), choices=ALL_TEXT_TYPES)
    class Meta:
        model = ResourceFile
        fields = ['name', 'desc', 'media_type', 'license', 'link']
        required = ['name', 'license']


# This allows paste to have a different set of options
FORMS = {1: ResourceEditPasteForm}

class ResourceAddForm(ResourceBaseForm):
    class Meta:
        model = ResourceFile
        fields = ['download', 'name']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and name[0] == '$':
            self.cleaned_data['name'] = name[1:].rsplit('.',1)[0].replace('_',' ').replace('-',' ').title()[:64]
        return self.cleaned_data['name']


class MirrorAddForm(ModelForm):
    class Meta:
        model  = ResourceMirror
        fields = ['name', 'url', 'capacity']

