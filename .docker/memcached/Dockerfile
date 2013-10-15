FROM ubuntu:12.04
MAINTAINER Amara "http://amara.org"
RUN (echo "deb http://archive.ubuntu.com/ubuntu precise main universe multiverse" > /etc/apt/sources.list)
RUN (echo "deb-src http://archive.ubuntu.com/ubuntu precise main universe multiverse" >> /etc/apt/sources.list)
RUN apt-get -qq update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y upgrade
RUN RUNLEVEL=1 DEBIAN_FRONTEND=noninteractive apt-get install -y wget gcc libevent-dev make
RUN wget https://s3.amazonaws.com/amara/support/memcached-1.4.15.tar.gz --no-check-certificate -O /tmp/pkg.tar.gz
RUN (cd /tmp && tar zxf pkg.tar.gz && cd memcached-* && ./configure --prefix=/usr/local && make install)
RUN rm -rf /tmp/*
EXPOSE 11211
CMD ["/usr/local/bin/memcached", "-u", "root", "-m", "64"]
