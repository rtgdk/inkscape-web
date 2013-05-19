#!/bin/bash

#TEST="--dry-run"
TEST=""
SOURCE="/home/doctormo/bazaar/inkscape-web"
TARGET="/var/www/staging.inkscape.org/"
EX="/var/www/staging.inkscape.org/keep-local.conf"

cd $SOURCE

bzr pull

rsync -rtuv $TEST --delete --exclude-from="$EX" . $TARGET

cd $TARGET

./pythonenv/bin/pip install -r utils/requirements.txt

./pythonenv/bin/python inkscape/manage.py syncdb
./pythonenv/bin/python inkscape/manage.py migrate

