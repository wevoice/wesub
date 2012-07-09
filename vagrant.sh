#!/bin/sh
VE_DIR='/opt/ve/unisubs'

cd /tmp
# install git
sudo apt-get update 2>&1 > /dev/null
sudo apt-get -y install git-core 2>&1 > /dev/null
# clone the puppet modules
git clone https://github.com/pculture/amara-puppet 2>&1 > /dev/null
if [ "$1" != "" ]; then
  echo "Checking out $1..."
  cd amara-puppet ; git checkout $1
  cd ..
fi

# run puppet
puppet apply --verbose --modulepath /tmp/amara-puppet/puppetmaster/modules /tmp/puppet/lucid64.pp

# create initial virtualenv if needed
if [ ! -d "$VE_DIR" ]; then
  virtualenv --no-site-packages --distribute $VE_DIR 2>&1 > /dev/null
  chown -R vagrant $VE_DIR
fi

# cleanup
rm -rf /tmp/amara-puppet
exit 0
