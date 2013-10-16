#!/bin/bash
source /usr/local/bin/config_env

cd $APP_DIR/deploy
$VE_DIR/bin/pip install -r requirements-test.txt

cd $APP_DIR
cp dev_settings_test.py test_settings.py
cat << EOF >> test_settings.py
BROKER_PORT = $TEST_BROKER_PORT
BROKER_USER = 'guest'
BROKER_PASSWORD = 'guest'

HAYSTACK_SOLR_URL = 'http://127.0.0.1:$TEST_SOLR_PORT/'
EOF

CMD="$VE_DIR/bin/python manage.py test search subtitles auth comments messages profiles statistic teams videos widget ted cogi apiv2 --settings=test_settings --with-xunit"

echo "Running Tests..."
$CMD
