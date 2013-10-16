#!/bin/bash
source /usr/local/bin/config_env

CMD="$VE_DIR/bin/python manage.py test search subtitles  auth comments messages profiles statistic teams videos widget ted cogi apiv2 --settings=test_settings --with-xunit"

echo "Running Tests..."
$CMD
