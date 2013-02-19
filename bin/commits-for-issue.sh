#!/usr/bin/env bash

# Outputs a list of commit links to our github account that are about a give
# issue, as long as you've started your commit messages with [ issue-number ]
if [ "$1" = "" ]; then 
    echo "You must specify issue number"; 
    exit 1
else
	git log --grep=^$1 --oneline  | cut -d " " -f1 |   sed 's/^/https:\/\/github.com\/pculture\/unisubs\/commit\//'
fi
exit 0
