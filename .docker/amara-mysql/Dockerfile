FROM ubuntu:12.04
MAINTAINER Amara "http://amara.org"
RUN (echo "deb http://archive.ubuntu.com/ubuntu precise main universe multiverse" > /etc/apt/sources.list)
RUN (echo "deb-src http://archive.ubuntu.com/ubuntu precise main universe multiverse" >> /etc/apt/sources.list)
RUN apt-get -qq update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y upgrade
RUN RUNLEVEL=1 DEBIAN_FRONTEND=noninteractive apt-get install -y wget
RUN wget https://s3.amazonaws.com/amara/support/mysql-5.1.72-linux-x86_64-glibc23.tar.gz --no-check-certificate -O /tmp/mysql.tar.gz
RUN (cd /tmp && tar zxf /tmp/mysql.tar.gz && mv mysql-* /usr/local/mysql && rm -rf /tmp/mysql*)
RUN (cd /usr/local/mysql && ./scripts/mysql_install_db > /dev/null 2>&1)
RUN (start-stop-daemon --start --pidfile /tmp/mysql.pid -b --exec /usr/local/mysql/bin/mysqld_safe -- --user=root && sleep 1 && echo "grant all privileges on *.* to 'root'@'%' identified by 'mysql' with grant option;" | /usr/local/mysql/bin/mysql)

EXPOSE 3306
CMD ["/usr/local/mysql/bin/mysqld_safe", "--user=root", "--bind-address=0.0.0.0"]

