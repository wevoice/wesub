#!/bin/sh
python manage.py syncdb --all --noinput
python manage.py migrate --fake
