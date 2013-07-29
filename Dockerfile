FROM ubuntu:12.04
MAINTAINER Evan Hazlett "ejhazlett@gmail.com"
RUN (echo "deb http://archive.ubuntu.com/ubuntu precise main universe multiverse" > /etc/apt/sources.list)
RUN apt-get -qq update
RUN apt-get -qq -y install wget python-dev python-setuptools make gcc s3cmd libmysqlclient-dev libmemcached-dev supervisor libxml2-dev libxslt-dev zlib1g-dev swig libssl-dev libyaml-dev git-core python-m2crypto
ENV REVISION staging
ADD . /opt/apps/unisubs
ADD .docker/setup.sh /tmp/setup.sh
RUN /bin/bash /tmp/setup.sh
ADD .docker/run.sh /usr/local/bin/run

EXPOSE 8000
CMD ["/bin/sh", "-e", "/usr/local/bin/run"]
