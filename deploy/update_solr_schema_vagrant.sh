#!/bin/bash

python manage.py build_solr_schema --settings=dev_settings > /etc/solr/conf/solr/solr.xml

/etc/init.d/tomcat6 restart

python manage.py rebuild_index --noinput --settings=dev_settings
