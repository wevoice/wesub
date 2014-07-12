#!/bin/sh
fig run --rm app python manage.py syncdb --all --noinput --settings=dev_settings
fig run --rm app python manage.py migrate --fake --settings=dev_settings
