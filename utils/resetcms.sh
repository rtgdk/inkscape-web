#!/bin/bash


wget http://staging.inkscape.org/media/content.json.gz -O /tmp/contents.json.gz
gunzip /tmp/contents.json.gz

./utils/jsonmigrator.py /tmp/contents.json > /tmp/content_reformed.json

./pythonenv/bin/python inkscape/manage.py reset --noinput cmsplugin_news cms

./pythonenv/bin/python inkscape/manage.py loaddata /tmp/content_reformed.json


