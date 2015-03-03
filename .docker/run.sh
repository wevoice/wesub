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
buffer-size = 32768
reload-on-as = 512
no-orphans = true
vacuum = true
pythonpath = $APP_ROOT
wsgi-file = $APP_DIR/deploy/unisubs.wsgi
static-map = /static=/usr/local/lib/python2.7/site-packages/django/contrib/admin/static
EOF

if [ ! -z "$NEW_RELIC_LICENSE_KEY" ] ; then
    pip install -U newrelic
    PRE="newrelic-admin run-program "
fi

$PRE $CMD
