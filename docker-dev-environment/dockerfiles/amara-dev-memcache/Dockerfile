FROM ubuntu:12.04
MAINTAINER Ben Dean-Kawamura <ben@pculture.org>

RUN DEBIAN_FRONTEND=noninteractive apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install memcached

CMD ["/usr/bin/memcached", "-u", "memcache"]
