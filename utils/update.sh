#!/bin/bash

#TEST="--dry-run"
TEST=""
SOURCE="/home/doctormo/bazaar/inkscape-web"
TARGET="/var/www/staging.inkscape.org/"
EX="/var/www/staging.inkscape.org/keep-local.conf"

SETTINGS="inkscape/settings.py"
REQUIRES="utils/requirements.txt"

PYTHON="./pythonenv/bin/python"
PIP="./pythonenv/bin/pip"

cd $SOURCE

bzr pull | grep Now\ on\ revision &> /dev/null
if [[ $? == 0 ]]; then
    echo "New revisions found, updating!"

    rsync -rtuv $TEST --delete --exclude-from="$EX" . $TARGET

    cd $TARGET

    if [ $REQUIRES -nt $PIP ]; then
        $PIP install -r $REQUIRES
    fi

    if [ $SETTINGS -nt "data/updated.last" ]; then
        $PYTHON inkscape/manage.py syncdb
        $PYTHON inkscape/manage.py migrate
        touch "data/updated.last"

        # Restart server like this:
        touch utils/wsgi_load.py
    fi
else
    echo "No new revisions, no update."
fi
