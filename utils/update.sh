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

python pythonenv/bin/pip -q install -r utils/requirements.txt

python inkscape/manage.py syncdb
python inkscape/manage.py migrate

