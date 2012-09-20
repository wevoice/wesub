#!/bin/bash

python manage.py build_solr_schema --settings=dev_settings > /etc/solr/conf/vagrant/conf/schema.xml

service tomcat6 restart

python manage.py rebuild_index --noinput --settings=dev_settings
