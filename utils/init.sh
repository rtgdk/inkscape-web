#!/bin/bash

virtualenv pythonenv
pip install -E pythonenv -r utils/requirements.txt
./inkscape/manage.py syncdb
./inkscape/manage.py migrate
./inkscape/manage.py migrate

