#!/bin/bash
AWS_ID=${AWS_ACCESS_ID:-}
AWS_KEY=${AWS_SECRET_KEY:-}
S3_PASSPHRASE=${S3_PASSPHRASE:-}
REV=${REVISION:-staging}
SETTINGS_REV=${SETTINGS_REVISION:-$REV}
APP_NAME=unisubs
APP_ROOT=/opt/apps
APP_DIR=$APP_ROOT/$APP_NAME
VE_ROOT=/opt/ve
VE_DIR=$VE_ROOT/$APP_NAME

if [ ! -z "$AWS_ID" ] && [ ! -z "$AWS_SECRET_KEY" ] ; then
    # create s3cfg
    cat << EOF > /etc/s3cfg
[default]
access_key = $AWS_ID
acl_public = False
bucket_location = US
cloudfront_host = cloudfront.amazonaws.com
cloudfront_resource = /2008-06-30/distribution
default_mime_type = binary/octet-stream
delete_removed = False
dry_run = False
encoding = UTF-8
encrypt = False
force = False
get_continue = False
gpg_command = /usr/bin/gpg
gpg_decrypt = %(gpg_command)s -d --verbose --no-use-agent --batch --yes --passphrase-fd %(passphrase_fd)s -o %(output_file)s %(input_file)s
gpg_encrypt = %(gpg_command)s -c --verbose --no-use-agent --batch --yes --passphrase-fd %(passphrase_fd)s -o %(output_file)s %(input_file)s
gpg_passphrase = $S3_PASSPHRASE
guess_mime_type = True
host_base = s3.amazonaws.com
host_bucket = %(bucket)s.s3.amazonaws.com
human_readable_sizes = False
list_md5 = False
preserve_attrs = True
progress_meter = True
proxy_host =
proxy_port = 0
recursive = False
recv_chunk = 4096
secret_key = $AWS_KEY
send_chunk = 4096
simpledb_host = sdb.amazonaws.com
skip_existing = False
urlencoding_mode = normal
use_https = False
verbosity = WARNING
EOF

    chown root:root /etc/s3cfg
    chmod 600 /etc/s3cfg

    mkdir -p /root/.ssh
    # get private key from s3 to clone private repo
    s3cmd -c /etc/s3cfg get --force s3://amara/admin/keys/git-pcf /root/.ssh/git_id_rsa
    chmod 600 /root/.ssh/git_id_rsa
    cat << EOF > /root/.ssh/config
Host github.com
    IdentityFile /root/.ssh/git_id_rsa
EOF
    cd $APP_DIR
    if [ ! -e "unisubs-integration" ]; then
        until git clone git@github.com:pculture/unisubs-integration.git ; do
            echo "Error during clone; trying again in 5 seconds..."
            sleep 5
        done
    fi
    s3cmd -c /etc/s3cfg get --force s3://amara/settings/$REV/server_local_settings.py server_local_settings.py
fi

# checkout respective revisions
cd $APP_DIR
git checkout $REV
if [ -e $APP_DIR/unisubs-integration ]; then
    cd $APP_DIR/unisubs-integration
    git pull --no-ff
    INTEGRATION_REV=`cat ../optional/unisubs-integration`
    git checkout $INTEGRATION_REV
fi
cd $APP_DIR
python ./deploy/create_commit_file.py

if [ "$UPDATE_VIRTUALENV" ]; then
    cd deploy
    # install dependencies
    $VE_DIR/bin/pip install -r requirements.txt
    # fix m2crypto
    rm -rf $VE_DIR/lib/python2.7/site-packages/M2Crypto
    ln -s /usr/lib/python2.7/dist-packages/M2Crypto $VE_DIR/lib/python2.7/site-packages/M2Crypto
    cd $APP_DIR
fi

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
EOF

uwsgi --ini $APP_ROOT/$APP_NAME.ini
