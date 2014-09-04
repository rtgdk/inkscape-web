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

from .models import Resource, ResourceFile, Gallery, Model
from .utils import ALL_TEXT_TYPES

class GalleryForm(ModelForm):
    class Meta:
        model = Gallery
        fields = ['name','group']

    def __init__(self, user, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        self.fields['group'].queryset = user.groups.all()


class ResourceBaseForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        if not isinstance(user, Model):
            raise AttributeError("User needs to be a model of a user.")
        self.user = user
        ModelForm.__init__(self, *args, **kwargs)
        if self.instance and 'owner' in self.fields:
            del self.fields['owner']
        if hasattr(self.Meta, 'required'):
            for key in self.Meta.required:
                self.fields[key].required = True

    def clean_owner(self):
        res = str(self.cleaned_data['owner'])
        if res not in ('1','2') and not self.instance:
            raise ValidationError(_("You need to have permission to post this work, or be the owner of the work."))
        return res == '1'

    def clean_download(self):
        if not self.instance or self.instance.download == self.cleaned_data['download']:
            # Don't stop editing of existing resources, with no space.
            return self.cleaned_data['download']

        space = self.user.quota() - self.user.resources.disk_usage()
        
        if self.cleaned_data['download'].size > space:
            raise ValidationError("Not enough space to upload this file.")
        return self.cleaned_data['download']

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

OWNS = (
  (0, _('No permission')),
  (1, _('I own the work')),
  (2, _('I have permission')),
)

class ResourceFileForm(ResourceBaseForm):
    owner = ChoiceField(choices=OWNS, label=_('Permission'))
    published = BooleanField(label=_('Publicly Visible'), required=False)

    class Meta:
        model = ResourceFile
        fields = ['name', 'desc', 'link', 'category', 'license', 'published', 'owner', 'download']
        required = ['name', 'desc', 'category', 'license']



class ResourcePasteForm(ResourceBaseForm):
    media_type = ChoiceField(label=_('Text Format'), choices=ALL_TEXT_TYPES)

    class Meta:
        model = ResourceFile
        fields = ['name', 'desc', 'media_type', 'link', 'license', 'download']
        required = ['name', 'license']

# This allows paste to have a different set of options
FORMS = {1: ResourcePasteForm}

class ResourceAddForm(ResourceBaseForm):
    class Meta:
        model = ResourceFile
        fields = ['download', 'name']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and name[0] == '$':
            self.cleaned_data['name'] = name[1:].rsplit('.',1)[0].replace('_',' ').replace('-',' ').title()[:64]
        return self.cleaned_data['name']

