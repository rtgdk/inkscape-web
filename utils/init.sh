#!/bin/bash

virtualenv pythonenv -p /usr/bin/python2.7

BIN="./pythonenv/bin"
PIP="$BIN/pip"
PYTHON="$BIN/python"

$PIP install -r utils/requirements.txt
$PYTHON ./inkscape/manage.py syncdb
$PYTHON ./inkscape/manage.py migrate

./utils/resetcms.sh


