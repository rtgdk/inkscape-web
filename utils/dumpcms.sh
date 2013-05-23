#!/bin/bash

cd /var/www/staging.inkscape.org/

./pythonenv/bin/python inkscape/manage.py dumpdata cms text menus mptt sekizai file picture snippet video twitter cmsplugin_news | gzip -9 > ./data/media/contents.json.gz

