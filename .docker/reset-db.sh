#!/bin/bash
source /usr/local/bin/config_env

cd $APP_DIR

python manage.py drop_all_tables
python manage.py syncdb --all --noinput
python manage.py migrate --fake
python manage.py setup_indexes
python manage.py setup_test_data
