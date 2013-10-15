#!/bin/bash

ROOT=`pwd`
AMARA=`docker images | grep amara`
if [ -z "$AMARA" ] ; then
    cd $ROOT && docker build -t amara .
    cd $ROOT/.docker/mysql && docker build -t amara-mysql .
    cd $ROOT/.docker/solr && docker build -t amara-solr .
    cd $ROOT/.docker/memcached && docker build -t amara-memcached .
    cd $ROOT/.docker/rabbitmq && docker build -t amara-rabbitmq .
fi

MYSQL=$(docker run -i -t -d amara-mysql)
MYSQL_PORT=$(docker port $MYSQL 3306)
SOLR=$(docker run -i -t -d amara-solr)
SOLR_PORT=$(docker port $SOLR 8983)
MEMCACHED=$(docker run -i -t -d amara-memcached)
MEMCACHED_PORT=$(docker port $MEMCACHED 11211)
RABBITMQ=$(docker run -i -t -d amara-rabbitmq)
RABBITMQ_PORT=$(docker port $RABBITMQ 5672)

echo "Containers: $MYSQL:$MYSQL_PORT $SOLR:$SOLR_PORT $MEMCACHED:$MEMCACHED_PORT $RABBITMQ:$RABBITMQ_PORT"

sleep 5

for CNT in "$MYSQL $SOLR $MEMCACHED $RABBITMQ"
do
    docker kill $CNT
    docker rm $CNT
done
