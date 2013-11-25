#!/bin/bash
# in order for this to work, you must have a ~/.transifexrc file (kept out of source control since it requires a passwords)
source /usr/local/bin/config_env

# Abort if any error
set -e

cd $APP_DIR
echo "Running makemessages"
$VE_DIR/bin/python manage.py makemessages -i deploy\* -i media\js\closure-library\* -i media/js/unisubs-calcdeps.js.py -a
$VE_DIR/bin/python manage.py makemessages -d djangojs -i deploy\* -i media\js\closure-library\* -i media/js/unisubs-calcdeps.js.py -a

echo "Uploading to transifex"
tx push --source

echo "Pulling from transifex"
tx pull -a

echo "Compiling messages"
$VE_DIR/bin/python manage.py compilemessages


echo "Committing and pushing to repository"
git add locale/*/LC_MESSAGES/django.*o
git commit -m "Updated transifex translations -- through update_translations.sh"
date
git push
