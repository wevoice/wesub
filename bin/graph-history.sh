#!/usr/bin/env bash

echo "from apps.subtitles.models import print_graphviz; print_graphviz('$1')" | python manage.py shell --settings=dev_settings > history.dot

dot -Tpng -ohistory.png history.dot
