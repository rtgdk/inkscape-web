#!/bin/bash
set -e

wget http://staging.inkscape.org/media/content.json.gz -O /tmp/contents.json.gz
gunzip -c /tmp/contents.json.gz \
 | ./utils/jsonmigrator.py - > /tmp/content_reformed.json

./pythonenv/bin/python inkscape/manage.py reset --noinput cms cmsplugin_news cmsplugin_pygments
./pythonenv/bin/python inkscape/manage.py loaddata /tmp/content_reformed.json
