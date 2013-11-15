FROM ubuntu:12.04
MAINTAINER Ben Dean-Kawamura <ben@pculture.org>

RUN DEBIAN_FRONTEND=noninteractive apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install wget default-jre-headless

WORKDIR /opt
RUN wget -q http://archive.apache.org/dist/lucene/solr/3.5.0/apache-solr-3.5.0.tgz
RUN tar zxf apache-solr-3.5.0.tgz
RUN rm apache-solr-3.5.0.tgz
ADD schema.xml /opt/apache-solr-3.5.0/example/solr/conf/schema.xml

CMD cd /opt/apache-solr-3.5.0/example && java -Dsolr.solr.home=solr -jar start.jar
