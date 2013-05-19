#!/bin/bash

virtualenv pythonenv

BIN="./pythonenv/bin"
PIP="$BIN/pip"
PYTHON="$BIN/python"

$PIP install -r utils/requirements.txt
$PYTHON ./inkscape/manage.py syncdb
$PYTHON ./inkscape/manage.py migrate
$PYTHON ./inkscape/manage.py migrate



