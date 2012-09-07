#!/bin/sh
APP_DIR='/opt/apps/vagrant/unisubs'
VE_DIR='/opt/ve/vagrant/unisubs'

cd /tmp
# install git
sudo apt-get update 2>&1 > /dev/null
sudo apt-get -y install git-core 2>&1 > /dev/null

# remove existing venv symlink (sifter #1379)
if [ -e "$APP_DIR/venv" ] ; then
  rm $APP_DIR/venv
fi

# create the puppet environment config files
echo "- vagrant\n" > /etc/system_environments.yml
echo "- vagrant\n" > /etc/system_roles.yml
# clone the puppet modules
git clone https://github.com/pculture/amara-puppet 2>&1 > /dev/null
if [ "$1" != "" ]; then
  echo "Checking out $1 branch of Amara Puppet..."
  cd amara-puppet ; git checkout $1
  cd ..
else
  # checkout production
  echo "Checking out production branch of Amara Puppet..."
  cd amara-puppet ; git checkout production
  cd ..
fi

# run puppet
puppet apply --verbose --modulepath /tmp/amara-puppet/puppetmaster/modules /tmp/puppet/lucid64.pp --reports=log

# create initial virtualenv if needed
if [ ! -d "$VE_DIR" ]; then
  virtualenv --no-site-packages --distribute $VE_DIR 2>&1 > /dev/null
  chown -R vagrant $VE_DIR
fi

# cleanup
rm -rf /tmp/amara-puppet
exit 0
