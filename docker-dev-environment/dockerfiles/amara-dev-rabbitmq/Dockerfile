FROM ubuntu:12.04
MAINTAINER Ben Dean-Kawamura <ben@pculture.org>

# Prevent upstart from starting services after apt-get installs them
ADD policy-rc.d /usr/sbin/policy-rc.d
RUN /bin/chmod 755 /usr/sbin/policy-rc.d

RUN DEBIAN_FRONTEND=noninteractive apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install curl
RUN curl http://www.rabbitmq.com/rabbitmq-signing-key-public.asc | apt-key add -
RUN echo "deb http://www.rabbitmq.com/debian/ testing main" > /etc/apt/sources.list.d/rabbitmq.list
RUN DEBIAN_FRONTEND=noninteractive apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install rabbitmq-server

EXPOSE 51002:5672

CMD ["/usr/sbin/rabbitmq-server"]
