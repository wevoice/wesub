#!/bin/bash
source /usr/local/bin/config_env

cd $APP_DIR
echo "Updating index..."
$VE_DIR/bin/python manage.py update_index --noinput --settings=unisubs_settings
