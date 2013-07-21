#!/bin/bash
set -e

BIN="./pythonenv/bin"
PIP="$BIN/pip"
PYTHON="$BIN/python"

$PIP install --upgrade distribute
$PIP install -r utils/requirements.txt
$PYTHON ./inkscape/manage.py syncdb
$PYTHON ./inkscape/manage.py migrate

