#!/bin/bash
source /usr/local/bin/config_env

PRE=""
CMD="uwsgi --ini $APP_ROOT/$APP_NAME.ini"

cat << EOF > $APP_ROOT/$APP_NAME.ini
[uwsgi]
master = true
workers = 4
harakiri = 20
max-requests = 5000
memory-report
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
logformat = [pid: %(pid)|app: ??|req: ??/??] %(addr) (%(user)) {%(vars) vars in %(pktsize) bytes} [%(ctime)] %(method) %(uri) => generated %(rsize) bytes in %(msecs) msecs (%(proto) %(status)) %(headers) headers in (hsize) bytes (%(switches) switches on core %(core)) body: %(body)
EOF

if [ ! -z "$NEW_RELIC_LICENSE_KEY" ] ; then
    pip install -U newrelic
    PRE="newrelic-admin run-program "
fi

$PRE $CMD
