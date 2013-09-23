FROM amara
MAINTAINER Ben Dean-Kawamura <ben@pculture.org>

RUN DEBIAN_FRONTEND=noninteractive apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install mysql-client
RUN /opt/ve/unisubs/bin/pip install mock nose django-nose
RUN mkdir -p /opt/extras/pictures
RUN mkdir -p /opt/extras/videos
ENV LC_ALL en_US.UTF-8
