#!/bin/bash
#
# Many pypi django/cms modules are broken in that they specify utf8
# instead of utf-8, gettext will freak out if the module specifies utf8
# So this file hacks it, we need it as a script because pythonenv means
# Files will be updated often and broken again.
#

find pythonenv/lib/ -name "*.py" -exec perl -pi -e 's/utf8/utf-8/g' {} \;


