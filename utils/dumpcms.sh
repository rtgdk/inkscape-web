#!/bin/bash

cd "$(dirname "$0")/../inkscape"

./manage.py dumpdata cms text menus mptt sekizai file picture snippet video twitter | gzip -9 &> ../data/media/contents.json.gz

