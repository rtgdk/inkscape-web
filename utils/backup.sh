#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"/..
BIN="$DIR/pythonenv/bin"
PYTHON="$BIN/python"
MANAGE="$DIR/inkscape/manage.py"
DEST="$DIR/data/backup"

mkdir -p $DEST/cms_db
mkdir -p $DEST/media

DATE=day-`date --iso`.json.gz

# Make a backup of the cms database and put it into a gz json file
# Don't make a copy of any other databases or tables from django.
$PYTHON $MANAGE dumpdata cms text menus mptt sekizai file picture \
                snippet video twitter cmsplugin_news \
    | gzip -9 > $DEST/cms_db/$DATED

cd $DEST/cms_db

# Create hard links of all the backups
ln -f $DATE "latest.json.gz"
ln -f $DATE week-`date +%Y-%W`.json.gz
ln -f $DATE month-`date +%Y-%M`.json.gz
ln -f $DATE year-`date +%Y`.json.gz

# Remove any days older than 14 days
rm `find . -name "day-*.json.gz" -mtime +14`

# Remove any weeks older than 6 weeks
rm `find . -name "week-*.json.gz" -mtime +42`

# Remove any months older than a year
rm `find . -name "month-*.json.gz" -mtime +256`

# Never remove year backups
# rm `find . -name "year-*.json.gz" -mtime +EEEE`

cd $DIR/data

# Make a backup of all the uploaded media here, archived once per week
cp -al media $DEST/media/`date +%Y-%W`

# There is room here for cleaning up old media uploads similar to the cms_db
