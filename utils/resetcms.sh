#!/bin/bash


wget http://staging.inkscape.org/media/content.json.gz -O /tmp/contents.json.gz
gunzip /tmp/contents.json.gz

./pythonenv/bin/python inkscape/manage.py reset --noinput cmsplugin_news cms

./pythonenv/bin/python inkscape/manage.py loaddata /tmp/contents.json


