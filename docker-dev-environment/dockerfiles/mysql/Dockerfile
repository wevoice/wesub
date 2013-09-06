FROM ubuntu:12.04
MAINTAINER Ben Dean-Kawamura <ben@pculture.org>

# Prevent upstart from starting services after apt-get installs them
ADD policy-rc.d /usr/sbin/policy-rc.d
RUN /bin/chmod 755 /usr/sbin/policy-rc.d

# install mysql
RUN DEBIAN_FRONTEND=noninteractive apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install mysql-server
RUN sed -i -e"s/^bind-address\s*=\s*127.0.0.1/bind-address = 0.0.0.0/" /etc/mysql/my.cnf
ADD setup-mysql.sh /tmp/setup-mysql.sh
RUN bash /tmp/setup-mysql.sh
RUN rm /tmp/setup-mysql.sh


EXPOSE 51000:3306

CMD ["/usr/sbin/mysqld"]
