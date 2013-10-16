#!/bin/bash

ROOT=`pwd`
for IMG in amara-app amara-mysql amara-solr amara-memcached amara-rabbitmq
do
    echo "Checking image $IMG..."
    if [ "`docker images | awk '{ print $1; }' | grep $IMG`" = "" ] ; then
        echo "Building $IMG image..."
        # check for top level image
        if [ "$IMG" = "amara-app" ] ; then
            cd $ROOT && docker build -t $IMG .
        else
            cd $ROOT/.docker/$IMG && docker build -t $IMG .
        fi
    fi
done

#MYSQL=$(docker run -i -t -d amara-mysql)
#MYSQL_PORT=$(docker port $MYSQL 3306)
SOLR=$(docker run -i -t -d amara-solr)
SOLR_PORT=$(docker port $SOLR 8983)
#MEMCACHED=$(docker run -i -t -d amara-memcached)
#MEMCACHED_PORT=$(docker port $MEMCACHED 11211)
RABBITMQ=$(docker run -i -t -d amara-rabbitmq)
RABBITMQ_PORT=$(docker port $RABBITMQ 5672)

echo "Containers: Solr:$SOLR:$SOLR_PORT RabbitMQ:$RABBITMQ:$RABBITMQ_PORT"

# run tests
docker run -i -t -e TEST_BROKER_PORT=$RABBITMQ_PORT -e TEST_SOLR_PORT=$SOLR_PORT amara-app /usr/local/bin/test_app

sleep 5

for CNT in $MYSQL $SOLR $MEMCACHED $RABBITMQ
do
    docker kill $CNT
    docker rm $CNT
done
