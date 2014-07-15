#!/bin/sh
fig run --rm app python manage.py syncdb --all --noinput
fig run --rm app python manage.py migrate --fake
