#!/bin/bash
source /usr/local/bin/config_env.sh

echo "$HOSTNAME" > /etc/mailname

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
smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
smtp_sasl_security_options = noanonymous
smtp_tls_security_level = may
header_size_limit = 4096000
EOF

/etc/init.d/postfix start

cd $APP_DIR
echo "Starting Worker..."
$VE_DIR/bin/python manage.py celeryd -E $* --scheduler=djcelery.schedulers.DatabaseScheduler --settings=unisubs_settings
