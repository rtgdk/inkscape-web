# Copied from django-annoying, sorry guys!

from django.db import models
from django.db.models import OneToOneField
from django.db.models.fields.related import SingleRelatedObjectDescriptor
from django.db.models.fields.files import ImageField, ImageFieldFile
from django.core.files.base import ContentFile

from PIL import Image

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO



class AutoSingleRelatedObjectDescriptor(SingleRelatedObjectDescriptor):
    def __get__(self, instance, instance_type=None):
        try:
            return super(AutoSingleRelatedObjectDescriptor, self).__get__(instance, instance_type)
        except self.related.model.DoesNotExist:
            obj = self.related.model(**{self.related.field.name: instance})
            obj.save()
            # Don't return obj directly, otherwise it won't be added
            # to Django's cache, and the first 2 calls to obj.relobj
            # will return 2 different in-memory objects
            return super(AutoSingleRelatedObjectDescriptor, self).__get__(instance, instance_type)


class AutoOneToOneField(OneToOneField):
    '''
    OneToOneField creates related object on first call if it doesnt exist yet.
    Use it instead of original OneToOne field.

    example:

        class MyProfile(models.Model):
            user = AutoOneToOneField(User, primary_key=True)
            home_page = models.URLField(max_length=255, blank=True)
            icq = models.IntegerField(max_length=255, null=True)
    '''
    def contribute_to_related_class(self, cls, related):
        setattr(cls, related.get_accessor_name(), AutoSingleRelatedObjectDescriptor(related))



def _update_ext(filename, new_ext):
    parts = filename.split('.')
    parts[-1] = new_ext
    return '.'.join(parts)


class ResizedImageFieldFile(ImageFieldFile):
    def save(self, name, content, save=True):
        new_content = StringIO()
        content.file.seek(0)

        img = Image.open(content.file)
        img.thumbnail((
            self.field.max_width,
            self.field.max_height
            ), Image.ANTIALIAS)
        img.save(new_content, format=self.field.format)

        new_content = ContentFile(new_content.getvalue())
        new_name = _update_ext(name, self.field.format.lower())

        super(ResizedImageFieldFile, self).save(new_name, new_content, save)


class ResizedImageField(ImageField):
    attr_class = ResizedImageFieldFile

    def __init__(self, name, max_width=100, max_height=100, format='PNG', *args, **kwargs):
        self.max_width = max_width
        self.max_height = max_height
        self.format = format
        super(ResizedImageField, self).__init__(name, *args, **kwargs)

