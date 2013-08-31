#!/bin/bash
source /usr/local/bin/config_env

PRE=""
CMD="uwsgi --ini $APP_ROOT/$APP_NAME.ini"

cat << EOF > $APP_ROOT/$APP_NAME.ini
[uwsgi]
master = true
workers = 4
http-socket = 0.0.0.0:8000
add-header = Node: $HOSTNAME
die-on-term = true
enable-threads = true
virtualenv = $VE_DIR
buffer-size = 32768
reload-on-as = 512
no-orphans = true
vacuum = true
pythonpath = $APP_ROOT
wsgi-file = $APP_DIR/deploy/unisubs.wsgi
env = DJANGO_SETTINGS_MODULE=unisubs_settings
static-map = /static=$VE_DIR/lib/python2.7/site-packages/django/contrib/admin/static
EOF

if [ ! -z "$NEW_RELIC_LICENSE_KEY" ] ; then
    $VE_DIR/bin/pip install -U newrelic
    PRE="$VE_DIR/bin/newrelic-admin run-program "
fi

$PRE $CMD
