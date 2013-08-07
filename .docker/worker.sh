#!/bin/bash
source /usr/local/bin/config_env.sh

cd $APP_DIR
echo "Starting Worker..."
$VE_DIR/bin/python manage.py celeryd -E $* --scheduler=djcelery.schedulers.DatabaseScheduler --settings=unisubs_settings
