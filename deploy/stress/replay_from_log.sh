#!/bin/bash


# USAGE: $0 <host> <logfile> "<start YYYY-mm-dd HH:MM:SS>" "<end YYYY-mm-dd HH:MM:SS>" [<api user name> <api key>]


#-----------------------------------------------------------------
# Constants
curl="curl --insecure --silent --location"


#-----------------------------------------------------------------
# Function performs a single request
replay_request() {
   local timestamp="$1"
   local verb="$2"
   local path="$3"

   case "$verb" in
      GET)
         echo "Replaying $timestamp"
         echo "   $verb $path"
         echo " "

         url="http://$host/$path"

         # Send extra headers if $api_user and $api_key are provided
         if [ -n "$api_user" -a -n "$api_key" ]; then
            result=`$curl -H "X-api-username: $api_user" -H "X-apikey: $api_key" $url`
         else
            result=`$curl $url`
         fi

         if [ "$?" != "0" -o -z "$result" ]; then
            echo $result
            echo "FAILURE RC $?"
            exit 1
         fi
         ;;

      POST)
         echo "SKIPPING $timestamp"
         echo "   $verb $path"
         echo " "
         ;;

      HEAD|OPTIONS)
         echo "SKIPPING $timestamp"
         echo "   $verb"
         echo " "
         ;;

      *)
         echo "INVALID $timestamp"
         echo "   $verb $path"
         echo " "
         ;;
   esac
}


#-----------------------------------------------------------------
# Function reads and processes a given log file
process_logfile() {
   local file="$1"
   local start="$2"
   local end="$3"

   #-----------------------------------------------------------------
   # Loop thru the file replaying only lines within the specified time range
   cat $file | while read line; do

      # Parse the log line to get timestamp
      local line_date=`echo $line | awk '{print $4}' | sed 's#\[##g'`

      local line_dd=`   echo $line_date | awk -F: '{print $1}' | awk -F '/' '{print $1}'`
      local line_month=`echo $line_date | awk -F: '{print $1}' | awk -F '/' '{print $2}'`
      local line_YYYY=` echo $line_date | awk -F: '{print $1}' | awk -F '/' '{print $3}'`

      local line_HH=`echo $line_date | awk -F: '{print $2}'`
      local line_MM=`echo $line_date | awk -F: '{print $3}'`
      local line_SS=`echo $line_date | awk -F: '{print $4}'`

      # Convert timestamp into seconds
      local line_seconds=`date +%s -d "${line_dd} ${line_month} ${line_YYYY} ${line_HH}:${line_MM}:${line_SS}"`

      # Parse the log line to get request
      local line_verb=`echo $line | awk '{print $6}' | sed 's#"##g'`
      local line_path=`echo $line | awk '{print $7}'`

      # Replay the request if timestamp is within range
      if [ $line_seconds -ge $start -a $line_seconds -le $end ]; then
         replay_request $line_date $line_verb $line_path
      fi

   done
}


#-----------------------------------------------------------------
# Command-line args
host="$1"
logfile="$2"
start_YYYY_mm_dd_HH_MM_SS="$3"
end_YYYY_mm_dd_HH_MM_SS="$4"
api_user="$5"
api_key="$6"

if [ -z "$end_YYYY_mm_dd_HH_MM_SS" ]; then
   echo "USAGE: $0 <host> <logfile> \"<start YYYY-mm-dd HH:MM:SS>\" \"<end YYYY-mm-dd HH:MM:SS>\" [<api user name> <api key>]"
   exit 1
fi

if [ ! -r "$logfile" ]; then
   echo "ERROR: Cannot read log file $logfile"
   exit 1
fi

#-----------------------------------------------------------------
# Convert the start and end times to seconds
start_seconds=`date +%s -d "$start_YYYY_mm_dd_HH_MM_SS"`
if [ -z "$start_seconds" ]; then
   #echo "Invalid start time: $start_YYYY_mm_dd_HH_MM_SS"
   exit 1
fi

end_seconds=`date +%s -d "$end_YYYY_mm_dd_HH_MM_SS"`
if [ -z "$end_seconds" ]; then
   #echo "Invalid end time: $end_YYYY_mm_dd_HH_MM_SS"
   exit 1
fi

#-----------------------------------------------------------------
process_logfile $logfile $start_seconds $end_seconds

exit
