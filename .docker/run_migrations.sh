#!/bin/bash
source /usr/local/bin/config_env

cd $APP_DIR
echo "Running migrations..."
$VE_DIR/bin/python manage.py migrate --settings=unisubs_settings
