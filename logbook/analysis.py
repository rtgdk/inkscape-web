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
Take parsed results and sort them into database objects.

Collapses lists into counts or averages as needed.
"""

from logbook.models import LogMetric, LogRequest, LogPeriod
from logbook.settings import get_setting
from django.db import transaction, utils

@transaction.atomic
def process_results(result, progress=None):
    """Each result is either an average or a count"""
    LogMetric.objects.clear_metrics()
    count = 0
    done = 0
    total = float(len(result))

    for count, path in enumerate(result):
        if progress:
            progress("save ", count / total, count, done)

        try:
            (request, _) = LogRequest.objects.get_or_create(path=path)
        except utils.IntegrityError:
            continue
        except utils.OperationalError:
            continue

        for d_ate, data in result[path].items():
            (period, _) = LogPeriod.objects.get_or_create(
                    period=0, date=d_ate, request_id=request.pk)
            for key, value in data.items():
                unit = get_setting('UNITS').get(key, None)
                metric = LogMetric.objects.get_metric(key, unit)
                period.values.create_or_update(metric, value)
                done += 1
    if progress:
        progress("save ", 1.0, count, done)


