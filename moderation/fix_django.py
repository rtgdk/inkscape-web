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
"""
Django ORM is very broken (1.6.5) when it comes to aggregations and then ordering.

This is because it is welding order_by, selects, extra select columns into a group_by
and causing MANY issues with the results being much more inconsistant and some queries
are rendered impossible because of it.

An argument could be made that ordering and selecting by a column that's grouped away
doesn't make sense. But this argument is flawed, because it ignores the effect of
super group sorting and first off the top access (i.e. Max/Min) to do top, bottom access.

This code should only effect flags, but it'd going to be run by everything calling sql
in your django project since it patches in code to the core of django. It might also
break in future versions of django. BEWARE!
"""

from django.db.models.sql.compiler import SQLCompiler

_old_method = SQLCompiler.get_grouping

def replacement_method(self, having_group_by, ordering_group_by):
    if 'moderation_flag' not in self.query.tables:
        return _old_method(self, having_group_by, ordering_group_by)

    qn = self.quote_name_unless_alias
    result, params = [], []
    seen = set()
    cols = self.query.group_by
    if cols and len(cols) > 4:
        # Worry here that django has done something crazy
        cols = [cols[-1]]
    for col in cols or []:
        col_params = ()
        if isinstance(col, (list, tuple)):
            sql = '%s.%s' % (qn(col[0]), qn(col[1]))
        elif hasattr(col, 'as_sql'):
            sql, col_params = col.as_sql(qn, self.connection)
        else:
            sql = '(%s)' % str(col)
        if sql not in seen:
            result.append(sql)
            params.extend(col_params)
            seen.add(sql)
    return result, params

SQLCompiler.get_grouping = replacement_method

