#!/bin/bash

mv locale/en/LC_MESSAGES/django.po locale/django.pot
cat ./utils/lang/list.txt | xargs -i1 mv locale/1/LC_MESSAGES/django.po locale/1.po

