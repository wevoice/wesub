#!/bin/bash
source /usr/local/bin/config_env
# install client
echo "Installing latest Transifex client..."
pip install transifex-client
# update
cd $APP_DIR
# get private key from s3 to clone private repo
s3cmd -c /etc/s3cfg get --force s3://amara/admin/keys/amara-transifex /root/.ssh/amara_transifex
chmod 600 /root/.ssh/amara_transifex
cat << EOF > /root/.ssh/config
Host github.com
    IdentityFile /root/.ssh/amara_transifex
EOF

cat << EOF > /root/.gitconfig
[user]
    name = transifex
    email = admin@amara.org
EOF

echo "Running makemessages"
python manage.py makemessages -i deploy\* -i media\js\closure-library\* -i media/js/unisubs-calcdeps.js.py -a
python manage.py makemessages -d djangojs -i deploy\* -i media\js\closure-library\* -i media/js/unisubs-calcdeps.js.py -a

echo "Uploading to transifex"
tx push --source

echo "Pulling from transifex"
tx pull -a -f

echo "Compiling messages"
python manage.py compilemessages

echo "Committing and pushing to repository"
date
git pull
git add locale/*/LC_MESSAGES/django.*o
git commit -m "Updated transifex translations -- through update_translations.sh"
git push
echo "Translations updated..."
