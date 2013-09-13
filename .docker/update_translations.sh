#!/bin/bash
source /usr/local/bin/config_env

cd $APP_DIR
# get private key from s3 to clone private repo
s3cmd -c /etc/s3cfg get --force s3://amara/admin/keys/amara-transifex /root/.ssh/amara_transifex
chmod 600 /root/.ssh/amara_transifex
cat << EOF > /root/.ssh/config
Host github.com
    IdentityFile /root/.ssh/amara_transifex
EOF

./deploy/update_translations.sh
