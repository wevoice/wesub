#!/bin/sh
echo "Compiling Media..."

APP_NAME=unisubs
APP_ROOT=/opt/apps
APP_DIR=$APP_ROOT/$APP_NAME
VE_ROOT=/opt/ve
VE_DIR=$VE_ROOT/$APP_NAME

cd $APP_DIR
$VE_DIR/bin/python manage.py compile_media --compilation-level=ADVANCED_OPTIMIZATIONS --settings=unisubs_settings
$VE_DIR/bin/python manage.py send_to_s3 --settings=unisubs_settings
