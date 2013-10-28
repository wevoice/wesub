#!/bin/bash
python manage.py build_solr_schema > schema.xml
cp -f schema.xml .docker/amara-solr/schema.xml
cp -f schema.xml docker-dev-environment/dockerfiles/amara-dev-solr/schema.xml
