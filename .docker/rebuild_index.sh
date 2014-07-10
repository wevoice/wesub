#!/bin/bash
source /usr/local/bin/config_env

cd $APP_DIR
echo "Rebuilding index..."
$VE_DIR/bin/python manage.py rebuild_index_ordered --noinput --settings=unisubs_settings
