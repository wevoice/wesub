#!/bin/bash
source /usr/local/bin/config_env

PRE=""
CMD="$VE_DIR/bin/python manage.py celeryd -E $CELERY_OPTS --scheduler=djcelery.schedulers.DatabaseScheduler --settings=unisubs_settings"

echo "$MAILNAME" > /etc/mailname

cat << EOF > /etc/postfix/main.cf
smtpd_banner = $HOSTNAME ESMTP $mail_name (Ubuntu)
biff = no
append_dot_mydomain = no
readme_directory = no
smtpd_tls_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
smtpd_tls_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
smtpd_use_tls=yes
smtpd_tls_session_cache_database = btree:${data_directory}/smtpd_scache
smtp_tls_session_cache_database = btree:${data_directory}/smtp_scache
myorigin = /etc/mailname
myhostname = $HOSTNAME
alias_maps = hash:/etc/aliases
alias_database = hash:/etc/aliases
mydestination = $HOSTNAME.ec2.internal, localhost.ec2.internal, , localhost
relayhost = [$SMTP_HOST]:$SMTP_PORT
mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128
mailbox_size_limit = 0
recipient_delimiter = +
inet_interfaces = all
smtp_sasl_auth_enable = yes
smtp_sasl_password_maps = static:$SASL_USER:$SASL_PASSWD
smtp_sasl_security_options = noanonymous
smtp_tls_security_level = may
header_size_limit = 4096000
EOF

/etc/init.d/postfix start

cd $APP_DIR
if [ ! -z "$NEW_RELIC_LICENSE_KEY" ] ; then
    $VE_DIR/bin/pip install -U newrelic
    PRE="$VE_DIR/bin/newrelic-admin run-program "
fi

echo "Starting Worker..."
$PRE $CMD
