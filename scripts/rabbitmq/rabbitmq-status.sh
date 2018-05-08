#!/bin/bash
#
# https://github.com/jasonmcintosh/rabbitmq-zabbix
#
#UserParameter=rabbitmq[*],<%= zabbix_script_dir %>/rabbitmq-status.sh
cd "$(dirname "$0")"

. .rab.auth

TYPE_OF_CHECK=$1
METRIC=$2
NODE=$3
VHOST=$4

if [[ -z "$HOSTNAME" ]]; then
    HOSTNAME=`hostname`
fi
if [[ -z "$NODE" ]]; then
    NODE=`hostname`
fi
if [[ -z "$VHOST" ]]; then
   VHOST='root'
fi
#rabbitmq[queues]
#rabbitmq[server,disk_free]
#rabbitmq[check_aliveness]

# This assumes that the server is going to then use zabbix_sender to feed the data BACK to the server.  Right now, I'm doing that
# in the python script

./api.py --hostname=$HOSTNAME --username=$USERNAME --password=$PASSWORD --check=$TYPE_OF_CHECK --metric=$METRIC --node="$NODE" --filters="$FILTER" --conf=$CONF  --loglevel=${LOGLEVEL} --logfile=${LOGFILE} --port=$PORT --vhost=$VHOST --protocol=$PROTOCOL

