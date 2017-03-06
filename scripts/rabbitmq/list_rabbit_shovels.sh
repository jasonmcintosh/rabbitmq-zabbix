#!/bin/bash
#
# https://github.com/jasonmcintosh/rabbitmq-zabbix
#
cd "$(dirname "$0")"
. .rab.auth

if [[ -z "$HOSTNAME" ]]; then
    HOSTNAME=`hostname`
fi
if [[ -z "$NODE" ]]; then
    NODE=`hostname`
fi


./api.py --username=$USERNAME --password=$PASSWORD --check=list_shovels --filter="$FILTER"  --hostname=$HOSTNAME --node="$NODE"  --conf=$CONF  --loglevel=${LOGLEVEL} --logfile=${LOGFILE} --port=$PORT --protocol=$PROTOCOL
