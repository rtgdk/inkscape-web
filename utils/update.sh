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

./pythonenv/bin/pip -q -r utils/requirements.txt

./puthonenv/bin/python inkscape/manage.py syncdb
./puthonenv/bin/python inkscape/manage.py migrate

