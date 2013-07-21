#!/bin/bash
set -e

virtualenv pythonenv -p /usr/bin/python2.7

./utils/refresh.sh
./utils/resetcms.sh


