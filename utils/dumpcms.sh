#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"/..
BIN="$DIR/pythonenv/bin"
PYTHON="$BIN/python"
MANAGE="$DIR/inkscape/manage.py"
DEST="$DIR/data/media/content"

mkdir -p $DEST

DATE=day-`date --iso`.json.gz

$PYTHON $MANAGE dumpdata cms text menus mptt sekizai file picture \
                snippet video twitter cmsplugin_news \
    | gzip -9 > $DEST/$DATED

cd $DEST

# Create hard links of all the backups
ln -f $DATE "latest.json.gz"
ln -f $DATE week-`date +%W`.json.gz
ln -f $DATE month-`date +%Y-%M`.json.gz
ln -f $DATE year-`date +%Y`.json.gz

# Remove any days older than 14 days
rm `find . -name "day-*.json.gz" -mtime +14`

# Remove any weeks older than 6 weeks
rm `find . -name "week-*.json.gz" -mtime +42`

# Remove any months older than a year
rm `find . -name "month-*.json.gz" -mtime +256`

# Never remove year backups

