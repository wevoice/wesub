FROM ubuntu:12.04
MAINTAINER Ben Dean-Kawamura <ben@pculture.org>

RUN (echo "deb http://archive.ubuntu.com/ubuntu precise main universe multiverse" > /etc/apt/sources.list)
RUN (echo "deb-src http://archive.ubuntu.com/ubuntu precise main universe multiverse" >> /etc/apt/sources.list)
RUN apt-get -qq update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y upgrade
RUN DEBIAN_FRONTEND=noninteractive apt-get -qq -y install wget python-dev python-setuptools make gcc s3cmd libmysqlclient-dev libmemcached-dev supervisor libxml2-dev libxslt-dev zlib1g-dev swig libssl-dev libyaml-dev git-core python-m2crypto subversion openjdk-6-jre libjpeg-dev libfreetype6-dev gettext mysql-client
# fix PIL
RUN ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib/
RUN ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib/
RUN ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib/
# install python modules
RUN /opt/ve/unisubs/bin/pip install mock nose django-nose
RUN mkdir -p /opt/extras/pictures
RUN mkdir -p /opt/extras/videos
ENV LC_ALL en_US.UTF-8
