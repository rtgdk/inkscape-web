#!/bin/bash

./utils/lang/unpack.sh

./utils/manage.py compilemessages $@

./utils/lang/pack.sh

