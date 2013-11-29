#!/bin/bash
source /usr/local/bin/config_env
# update
cd $APP_DIR
# get private key from s3 to clone private repo
s3cmd -c /etc/s3cfg get --force s3://amara/admin/keys/amara-transifex /root/.ssh/amara_transifex
chmod 600 /.ssh/amara_transifex
cat << EOF > /.ssh/config
Host github.com
    IdentityFile /root/.ssh/amara_transifex
EOF

cat << EOF > /.gitconfig
[user]
    name = transifex
    email = admin@amara.org
EOF

./deploy/update_translations.sh
