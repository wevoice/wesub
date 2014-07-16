#!/bin/bash
fig run --rm app python manage.py test --settings=dev_settings_test "$@"
