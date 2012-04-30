#!/bin/bash

# USAGE: $0 <api user name> <api key> <partner> [ <num trials> ]


#------------------------------
# Constants
host="staging.universalsubtitles.org"
curl="curl --insecure --progress-bar"

#------------------------------
# Command-line args
api_user="$1"
api_key="$2"
partner="$3"
ntrials=$4

if [ -z "$partner" ]; then
   echo "USAGE: $0 <api user name> <api key> <partner> [ <num trials> ]"
   exit 1
fi

if [ -z "$ntrials" ]; then
   ntrials="20"
fi

# This URL does not appear to reproduce failure
#url="https://$host/api2/$partner/videos/?format=json"

#------------------------------
# Stress API
for (( i = 1; i <= $ntrials; i++ )); do
   echo "`date`: Trial $i"

   url="https://$host/api2/$partner/videos/$i/languages/?format=json&offset=0&limit=100"
   result=`$curl -H "X-api-username: $api_user" -H "X-apikey: $api_key" $url`

   if [ "$?" != "0" ]; then
      echo "FAILURE CURL RC $? ON TRIAL $i"
      exit 1
   fi

   if [ -z "`echo $result | grep subtitle`" ]; then
      echo "FAILURE IN RESULT STRING ON TRIAL $i"
      echo "$curl -H \"X-api-username: $api_user\" -H \"X-apikey: $api_key\" $url"
      echo " "
      echo $result
      exit 1
   fi

   result=""
done

