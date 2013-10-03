FROM amara
MAINTAINER Ben Dean-Kawamura <ben@pculture.org>

ADD sources.list /etc/apt/sources.list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE49EC21
RUN apt-get -qq update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -qq -y  mysql-client firefox flashplugin-installer python-virtualenv xvfb
# install python packages for the dev environment
RUN /opt/ve/unisubs/bin/pip install mock nose django-nose selenium factory_boy

ENV LC_ALL en_US.UTF-8
