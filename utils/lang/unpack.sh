#!/bin/bash

mv locale/django.pot locale/en/LC_MESSAGES/django.po
cat ./utils/lang/list.txt | xargs -i1 mv locale/1.po locale/1/LC_MESSAGES/django.po

