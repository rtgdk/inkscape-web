#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"/..
BIN="$DIR/pythonenv/bin"
PYTHON="$BIN/python"
MANAGE="$DIR/inkscape/manage.py"

$PYTHON $MANAGE dumpdata cms text menus mptt sekizai file picture \
                snippet video twitter cmsplugin_news \
    | gzip -9 > $DIR/data/media/contents.json.gz

