#!/usr/bin/python
"""
Open django json dumps and update them to the latest versions so they
can be continued to be used as backups going forwards.

Usage: ./utils/jsonmigrator.py <content.json>
"""

import os
import sys
import json

def delete(data, field):
    if data.has_key(field):
        data.pop(field)
        return True
    return False

UPDATES = {
  'cms.page': (
    [ delete, 'moderator_state' ],
  ),
}


def update(content, updates):
    WARNED = []
    COUNT = {}

    for item in content:
        model = item['model']
        update = updates.get(model, [])

        if not update:
            if model not in WARNED:
                sys.stderr.write("No updates for %s\n" % model)
                WARNED.append(model)
            continue
        COUNT[model] = COUNT.setdefault(model, {})
        for up in update:
            if up[0](item['fields'], *up[1:]):
                COUNT[model][up[1]] = COUNT[model].setdefault(up[1], 0) + 1

    for model, counts in COUNT.iteritems():
        sys.stderr.write("Updated %s: %s\n" % (model, str(counts)))


if __name__ == '__main__':
    if len(sys.argv) == 1 or not os.path.exists(sys.argv[1]):
        sys.stderr.write(__doc__)
        sys.exit(1)

    with open(sys.argv[1], 'r') as fhl:
        content = json.loads(fhl.read())
    update(content, UPDATES)
    print json.dumps(content)

