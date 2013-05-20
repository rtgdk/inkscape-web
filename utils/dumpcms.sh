#!/bin/bash

#cd "$(dirname "$0")/../inkscape"

./pythonenv/bin/python inkscape/manage.py dumpdata cms text menus mptt sekizai file picture snippet video twitter cmdplugin_news | gzip -9 &> ../data/media/contents.json.gz

