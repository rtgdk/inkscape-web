#
# Copyright 2016, Martin Owens <doctormo@gmail.com>
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
"""
Models for the logbook app, stores:

    - Files processed
    - Requests (urls accessed)
    - Metrics (facets about a request)
    - Periods (aggregations of time)
    - Values (total counts or verages of those periods)

"""

from datetime import date, timedelta
from collections import defaultdict, Counter

from django.conf import settings
from django.db.models import *

from django.core.urlresolvers import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

class LogFile(Model):
    """Simple inode recorder to check if log file has been done"""
    inode = PositiveIntegerField(unique=True, db_index=True)
    touched = DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.inode)


class LogRequest(Model):
    path = CharField(max_length=255, unique=True, db_index=True, null=True)

    class Meta:
        ordering = ['path']

    def __str__(self):
        if self.path is not None:
            return self.path.encode('utf-8')
        return "Logs"

    @property
    def slug(self):
        return '_' + self.path.replace('/', '_')

    def get_absolute_url(self):
        if self.path is None:
            return reverse('logbook:sitewide')
        return reverse('logbook:request', kwargs={'path': self.slug})

    def days(self, **kwargs):
        return list(self.subset(0, 30, **kwargs))
    def week_days(self, **kwargs):
        return list(self.subset(1, **kwargs))
    def weeks(self, **kwargs):
        return list(self.subset(2, 70, **kwargs))
    def months(self, **kwargs):
        return list(self.subset(3, 31 * 12, **kwargs))
    def years(self, **kwargs):
        return list(self.subset(4, **kwargs))

    def subset(self, period, days=None, today=0, family=None):
        """Returns thirty days of daily data"""
        qs = self.periods.filter(period=period)

        # Adjust subset's date by number of interations,
        # or by a fixed date object offset.
        if isinstance(today, int):
            today = now() - timedelta(days * today)
        if days is not None:
            qs = qs.filter(date__lt=today, date__gte=today - timedelta(days))

        for metric in LogMetric.objects.all():
            if metric.is_count:
                yield (metric,) + self.get_set(qs, metric, family=family)

    def get_set(self, qs, metric, family=None):
        limit = 10
        vqs = metric.values.filter(period__in=qs)

        if metric.is_range:
            # Ranges should never have more than one item
            return qs.order_by('-avg').values_list('period__date', 'avg', 'low', 'high')

        look = 'name__name'
        if metric.has_family and family is None:
            look = 'name__family'
        elif family is not None:
            qs = qs.filter(name__family=family)

        names = vqs.values_list(look).annotate(count=Sum('count')).order_by('-count')\
                    .values_list(look, flat=True)[:limit]

        values = defaultdict(dict)
        for (dt, name, count) in  vqs.values_list('period__date', look)\
                .annotate(count=Sum('count')).order_by('-count')[:limit]:
            values[dt][name] = count

        sorted_v = []
        for dt in sorted(values):
            sorted_v.append((dt, [values[dt].get(name, 0) for name in names]))
        return (names, sorted_v)


class MetricManager(Manager):
    CACHE = {}
    def clear_metrics(self):
        """Remove all cached metrics"""
        self.CACHE = {}

    def get_metric(self, key, unit=None):
        """
        Returns (and creates if it doesn't already exist) a metric
        based on the key and will save the units used 
        """
        if key not in self.CACHE:
            self.CACHE[key] = self.get_or_create(name=key,
                  defaults={'label': key.title(), 'unit': unit})[0]
        return self.CACHE[key]


class LogMetric(Model):
    name = SlugField(max_length=32, unique=True)
    unit = CharField(max_length=8, blank=True, null=True)
    label = CharField(max_length=32)
    has_family = BooleanField(default=False)

    is_range = property(lambda self: bool(self.unit))
    is_count = property(lambda self: not self.is_range)

    objects = MetricManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.label.encode('utf-8')

    def families(self):
        for family in set(self.values.values_list('name__family', flat=True)):
            nr = self.values.filter(name__family=family).values_list('name__name').annotate(count=Sum('count')).order_by('-count')
            yield (family, nr)


class LogPeriod(Model):
    FORMAT = ["%Y-%m-%d", "%l", "%Y@%w", "%Y-%m", "%Y"]
    PERIODS = (
      (0, 'Day'),
      (1, 'Week Day'),
      (2, 'Week of Year'),
      (3, 'Month'),
      (4, 'Year'),
    )
    date = DateField(db_index=True)
    period = IntegerField(choices=PERIODS, default=0)
    request = ForeignKey(LogRequest, related_name='periods')

    class Meta:
        unique_together = ('period', 'date', 'request')
        ordering = ['period', 'date', 'request']

    def __str__(self):
        return "/%s in %s" % (str(self.request), self.label)

    @property
    def label(self):
        """Return a useful label for this period"""
        return self.date.strftime(self.FORMAT[self.period])

    def get_periods(self):
        """Return a LogPeriod for each aggregated period"""
        rq = dict(request_id=self.request_id)
        qs = LogPeriod.objects.filter(period=0, **rq)
        dt = self.date

        wday = dt.weekday()
        yield qs.filter(date__week_day=wday), \
              dict(period=1, date=date(2016, 2, wday+1), **rq)

        week = dt - timedelta(dt.isocalendar()[2])
        yield qs.filter(date__gte=week, date__lt=week + timedelta(7)), \
              dict(period=2, date=week, **rq)

        month = date(dt.year, dt.month, 1)
        yield qs.filter(date__month=dt.month), \
              dict(period=3, date=month, **rq)

        year = date(dt.year, 1, 1)
        yield qs.filter(date__year=dt.year), \
              dict(period=4, date=year, **rq)


class NameManager(Manager):
    def get_name(self, name):
        if isinstance(name, tuple):
            (family, name) = name
        else:
            (family, name) = (None, name)

        df = {'re_name': name, 're_family': family}
        return self.get_or_create(name=name, family=family, defaults=df)[0]


class LogName(Model):
    """
    A name is a single non-number based value with which a count is
    attached with the LogValue. A Metric can have a number of names.
    """
    name = CharField(max_length=255, db_index=True)
    family = CharField(max_length=128, db_index=True, null=True)

    re_name = CharField(max_length=255, db_index=True,
            help_text="Rename this metric value to something else.")
    re_family = CharField(max_length=255, db_index=True, null=True, blank=True,
            help_text="Rename this family to something else.")

    objects = NameManager()

    class Meta:
        unique_together = ('name', 'family')
        ordering = ['name', 'family']

    def __str__(self):
        if self.family:
            return "%s %s" % (self.family, self.name)
        return self.name


class ValueManager(Manager):
    """Provide ways of updating values"""

    def create_or_update(self, metric, values):
        """Like get_or_create, but specialised"""
        names = LogName.objects.get_name

        if metric.is_range:
            return self.new_average(metric, [int(v) for v in values])

        for name, value in Counter(values).items():
            self.new_value(metric, names(name), count=int(value))

    def new_average(self, metric, values):
        (low, high, count) = (min(values), max(values), len(values))
        avg = sum(values) / float(count)
        self.new_value(metric, count=count, low=low, high=high, avg=avg)

    def new_value(self, metric, name=None, **kwargs):
        """Create count value or update as needed"""
        name_id = name.pk if name else None
        (log, new) = self.get_or_create(metric_id=metric.pk,
                                        name_id=name_id, defaults=kwargs)
        if not new:
            log.update_value(**kwargs)
        log.regenerate()


class LogValue(Model):
    """
    Log Value can record either a dictionary count or a range (with no name).
    For week/month/year periods it records the ranged dictionary count.

    Family is a grouping for names, for example:
      metric=browser, name=Firefox 44.0 family=firefox
    """
    period = ForeignKey(LogPeriod, related_name='values')
    metric = ForeignKey(LogMetric, related_name='values')
    name   = ForeignKey(LogName, related_name='values', null=True)

    count = PositiveIntegerField(default=0)
    high = PositiveIntegerField(null=True)
    low = PositiveIntegerField(null=True)
    avg = PositiveIntegerField(null=True)

    objects = ValueManager()

    class Meta:
        unique_together = ('metric', 'period', 'name')
        ordering = ['metric', 'period', 'name']

    def __str__(self):
        return "%s on %s (%s=%s)" % (self.metric, self.period,
                                     self.name, self.count)

    def update_value(self, count, low=None, high=None, avg=None):
        """Update an existing log entry"""
        if avg is not None:
            total = (self.avg * self.count + avg * count)
            self.avg = total / (self.count + count)
            self.low = min([low, self.low])
            self.high = max([high, self.high])
        self.count += count
        self.save()

    def regenerate(self):
        """Calculate the weekly, yearly periods"""
        for periods, period_dict in self.period.get_periods():
            period_ids = periods.values_list('id', flat=True)
            if len(period_ids) <= 1:
                continue

            qs = LogValue.objects.filter(metric_id=self.metric_id,
                      name_id=self.name_id, period_id__in=period_ids)
            if qs.count() <= 1:
                continue

            (out, _) = LogPeriod.objects.get_or_create(**period_dict)

            (item, _) = LogValue.objects.get_or_create(metric_id=self.metric_id,
                    period_id=out.pk, name_id=self.name_id)

            if self.name:
                # Values with names are simple counts
                data = qs.aggregate(count=Sum('count'), low=Min('count'),
                           high=Max('count'), avg=Avg('count'))
            else:
                # Without names they are averages (for example, bytes)
                data = qs.aggregate(count=Sum('count'), low=Min('low'),
                           high=Max('high'), avg=Sum('avg') / Sum('count'))

            if data['count'] > 1:
                # Qickest way of updating a single item in django, (weird huh)
                LogValue.objects.filter(pk=item.pk).update(**data)

