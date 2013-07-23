#!/bin/bash

GOTO="/tmp/anti-msg-stash"
mkdir -p $GOTO
mv pythonenv $GOTO/

./utils/lang/unpack.sh

# pythonenv is gone, don't use it here
./inkscape/manage.py makemessages -a $@

./utils/lang/pack.sh

mv $GOTO/* .
rmdir $GOTO

