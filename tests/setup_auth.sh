#!/bin/sh

cat<<EOF>scripts/rabbitmq/.rab.auth
USERNAME=guest
PASSWORD=guest

LOGFILE=/tmp/rabbitmq_zabbix.log
LOGLEVEL=DEBUG

HOSTNAME=localhost
PORT=15672

EOF
