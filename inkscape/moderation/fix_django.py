"""
Django ORM is very broken (1.6.5) when it comes to aggregations and then ordering.

This is because it is welding order_by, selects, extra select columns into a group_by
and causing MANY issues with the results being much more inconsistant and some queries
are rendered impossible because of it.

An argument could be made that ordering and selecting by a column that's grouped away
doesn't make sense. But this argument is flawed, because it ignores the effect of
super group sorting and first off the top access. (which is what SQL DBs do)

We're NOT being careful here and we believe the functionality in django is WRONG.
Including this code in your project may result in some third party apps failing.
But we've never seen any that do fail.
"""

from django.db.models.sql.compiler import SQLCompiler

_old_method = SQLCompiler.get_grouping

def replacement_method(self, having_group_by, ordering_group_by):
    if 'moderation_flag' not in self.query.tables:
        return _old_method(self, having_group_by, ordering_group_by)

    qn = self.quote_name_unless_alias
    result, params = [], []
    seen = set()
    cols = self.query.group_by# + having_group_by + select_cols
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

