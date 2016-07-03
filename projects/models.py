#
# Copyright 2014, Martin Owens <doctormo@gmail.com>
#
# This file is part of the software inkscape-web, consisting of custom 
# code for the Inkscape project's django-based website.
#
# inkscape-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# inkscape-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with inkscape-web.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import datetime

from django.conf import settings

from django.db.models import *

from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.utils.text import slugify

from django.contrib.contenttypes.models import ContentType

from django.core.urlresolvers import reverse
from django.core.validators import MaxLengthValidator

from pile.models import null
from pile.fields import ResizedImageField

# Thread-safe current user middleware getter.
from cms.utils.permissions import get_current_user as get_user

class ProjectType(Model):
    value = CharField(_('Type Name'), max_length=128)

    def __str__(self):
        return self.value


class Project(Model):
    """A project details work that needs to be done"""
    
    DIFFICULTIES = (
      (0, _('Unknown')),
      (1, _('Easy')),
      (2, _('Moderate')),
      (3, _('Hard')),
      (4, _('Very hard')),
    )
    
    LOGO   = os.path.join(settings.STATIC_URL, 'images', 'project_logo.png')
    BANNER = os.path.join(settings.STATIC_URL, 'images', 'project_banner.png')
    
    sort   = IntegerField(_('Difficulty'), choices=DIFFICULTIES, default=2)
    title  = CharField(_('Title'), max_length=100)
    pitch  = CharField(_('Short Summary'), max_length=255, **null)
    slug   = SlugField(unique=True)
    desc   = TextField(_('Description'), validators=[MaxLengthValidator(50192)], **null)

    banner   = ResizedImageField(_("Banner (920x120)"), max_height=120, max_width=920,
                                                        min_height=90, min_width=600,
                          upload_to=os.path.join('project', 'banner'), default=BANNER)
    logo     = ResizedImageField(_("Logo (150x150)"), max_height=150, max_width=150,
                                                      min_height=150, min_width=150,
                          upload_to=os.path.join('project', 'logo'), default=LOGO)

    duration = IntegerField(_('Expected Duration in Days'), default=0)
    started  = DateTimeField(**null)
    finished = DateTimeField(**null)

    created  = DateTimeField(auto_now_add=True, db_index=True)
    edited   = DateTimeField(auto_now=True)

    proposer = ForeignKey(settings.AUTH_USER_MODEL, related_name='proposed_projects', default=get_user)
    manager  = ForeignKey(settings.AUTH_USER_MODEL, related_name='manages_projects', **null)
    reviewer = ForeignKey(settings.AUTH_USER_MODEL, related_name='reviews_projects', **null)
    second   = ForeignKey(settings.AUTH_USER_MODEL, related_name='seconds_projects', **null)

    project_type = ForeignKey(ProjectType)

    is_fundable = BooleanField(default=False)
    is_approved = BooleanField(_('Pre-approved'), default=False)

    criteria = ManyToManyField('Criteria', blank=True)

    def __str__(self):
        return self.title

    def save(self, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        Model.save(self, **kwargs)

    def progress(self):
        """Returns a float, percentage of completed deliverable items"""
        count = self.deliverables.all().count()
        if count:
            done = self.deliverables.filter(finished__isnull=False).count()
            if done > 0:
              return (done / float(count)) * 100.0
        return self.finished and 100.0 or 0.0

    def get_absolute_url(self):
        return reverse('project', kwargs={'slug': self.slug})

    def get_status(self):
      """Returns a (preliminary) status number / string tuple for displaying in templates
      possible status include: proposed (needs review), application phase (free to take), 
      in progress, finished. The number could be used for CSS classing."""
      
      if self.manager is None:
          return (1, _("Proposed"))
      elif self.started is None:
          return (2, _("Application Phase"))
      elif self.started is not None:
          return (3, _("In Progress"))
      elif self.finished is not None:
          return (4, _("Completed"))
      else:
          return (0, _("Undetermined"))

    def get_expected_enddate(self):
        if self.started is not None:
            return self.started + datetime.timedelta(days=self.duration)
        else:
            return datetime.datetime.now() + datetime.timedelta(days=self.duration)

    #@property
    #def people(self):
      #"""Can be used to send update emails to everyone involved, or for filtering"""
      #all_people = []
      #all_workers = [worker.user for worker in self.workers.all()]
      #for person in [self.proposer, self.manager, self.reviewer, self.second] + all_workers:
        #if person is not None:
          #all_people.append(person)
      #return all_people
      
      
class Worker(Model):
    """Acts as both a statement of assignment and application process"""
    project  = ForeignKey(Project, related_name='workers')
    user     = ForeignKey(settings.AUTH_USER_MODEL, related_name='works')

    plan     = TextField(validators=[MaxLengthValidator(8192)], **null)

    created  = DateTimeField(auto_now_add=True, db_index=True)
    vetted   = DateTimeField(**null)
    assigned = BooleanField(default=False)

    def __str__(self):
        p = (str(self.user), str(self.project))
        if not self.assigned:
            return "%s application for %s" % p
        return "%s working on %s" % p 


class Deliverable(Model):
    """A single deliverable item"""
    project  = ForeignKey(Project, related_name='deliverables')
    name     = CharField(_('Deliverable'), max_length=255)
    sort     = IntegerField(default=0)

    targeted = DateField(**null)
    finished = DateField(**null)
    
    class Meta:
        ordering = 'sort',

    def __str__(self):
        return self.name


class Task(Model):
    """A task or sub-task of a deliverable stage"""
    delive = ForeignKey(Deliverable, related_name='tasks')
    name   = CharField(_('Task'), max_length=255)

    targeted = DateField(**null)
    finished = DateField(**null)
    
    class Meta:
        ordering = 'targeted',

    def __str__(self):
        return self.name


class Criteria(Model):
    content  = CharField(_('Criteria'), max_length=255)
    detail   = TextField(validators=[MaxLengthValidator(4096)], **null)
    
    def __str__(self):
        return self.content


class ProjectUpdate(Model):
    """A project should always have at least one update with its primary description"""

    project  = ForeignKey(Project, related_name='updates')
    describe = TextField(_("Description"), validators=[MaxLengthValidator(12288)])
    image    = ResizedImageField(_("Image"), max_height=400, max_width=400,
                     upload_to=os.path.join('project', 'update', '%Y'), **null)

    creator  = ForeignKey(settings.AUTH_USER_MODEL, default=get_user)
    created  = DateTimeField(auto_now_add=True, db_index=True)
    edited   = DateTimeField(auto_now=True)

    def __str__(self):
        return self.describe
      
class RelatedFile(Model):
    """Allows to add files to Project Update reports"""
    
    for_update = ForeignKey(ProjectUpdate, related_name='related_files')
    updatefile = FileField(_("Related File"), upload_to=os.path.join('project', 'related_files'))
                           
    def __str__(self):
        return self.updatefile.filename
