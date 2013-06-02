#!/bin/bash


wget http://staging.inkscape.org/media/content.json.gz -O /tmp/contents.gz
gunzip /tmp/content.gz

./pythonenv/bin/python inkscape/manage.py reset cmsplugin_news cms

./pythonenv/bin/python inkscape/manage.py loaddata /tmp/contents.json


