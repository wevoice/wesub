#!/bin/bash
source /usr/local/bin/config_env

cd $APP_DIR
echo "Running migrations..."
python manage.py migrate --settings=unisubs_settings
