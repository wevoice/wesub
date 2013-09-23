#!/bin/sh

iptables -t nat -F
ifconfig docker0 down
brctl delbr docker0
service docker restart
