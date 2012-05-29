#!/bin/bash

# USAGE: $0 <api user name> <api key> <partner> <file containing video ids one-per-line>

# Note: when run from multiple concurrent windows, this can stress app server CPU


#------------------------------
# Constants
host="staging.universalsubtitles.org"
curl="curl --insecure --progress-bar"

#------------------------------
# Command-line args
api_user="$1"
api_key="$2"
partner="$3"
filename="$4"

if [ -z "$filename" -o ! -r "$filename" ]; then
   echo "USAGE: $0 <api user name> <api key> <partner> <file containing video ids one-per-line>"
   exit 1
fi

# This URL does not appear to reproduce failure
#url="https://$host/api2/$partner/videos/?format=json"

#------------------------------
# Stress API
i=1
cat $filename | while read line; do
   video_id=`echo $line | awk '{print $1}'`
   echo "`date`: Trial $i video ID $video_id"

   url="https://$host/api2/$partner/videos/$video_id/languages/?format=json&offset=0&limit=1000"
   result=`$curl -H "X-api-username: $api_user" -H "X-apikey: $api_key" $url`

   if [ "$?" != "0" ]; then
      echo "FAILURE CURL RC $? ON TRIAL $i"
      exit 1
   fi

   if [ -z "$result" -o -z "`echo $result | grep total_count`" ]; then
      echo "FAILURE IN RESULT STRING ON TRIAL $i"
      echo "$curl -H \"X-api-username: $api_user\" -H \"X-apikey: $api_key\" $url"
      echo " "
      echo $result
      exit 1
   fi

   result=""
   i=`expr $i + 1`
done

