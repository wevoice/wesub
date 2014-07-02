#!/bin/bash
. /etc/environment

APP_NAME=unisubs
APP_ROOT=/opt/apps
APP_DIR=$APP_ROOT/$APP_NAME
VE_ROOT=/opt/ve
VE_DIR=$VE_ROOT/$APP_NAME
SETUPTOOLS_URL=https://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz
BUILD_DIR=/var/tmp
CLOSURE_PATH=/opt/google-closure

mkdir -p $APP_ROOT
mkdir -p $VE_ROOT

# install pip
easy_install pip

pip install uwsgi virtualenv

# install google closure
git clone https://github.com/google/closure-library $CLOSURE_PATH
pushd $CLOSURE_PATH && git checkout adbcc8ef6530ea16bac9f877901fe6b32995c5ff
popd
# symlink for compilation
ln -sf $CLOSURE_PATH $APP_DIR/media/js/closure-library

# host key for github
mkdir -p /root/.ssh
cat << EOF > /root/.ssh/known_hosts
github.com,207.97.227.239 ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==
EOF

# create ve
if [ ! -e "$VE_DIR" ]; then
    cd $APP_DIR
    virtualenv --no-site-packages $VE_DIR
    cd deploy
    $VE_DIR/bin/pip install -r requirements.txt
    # fix m2crypto
    rm -rf $VE_DIR/lib/python2.7/site-packages/M2Crypto
    ln -s /usr/lib/python2.7/dist-packages/M2Crypto $VE_DIR/lib/python2.7/site-packages/M2Crypto
fi

