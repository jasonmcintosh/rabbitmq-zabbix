#!/bin/bash
#UserParameter=rabbitmq[*],<%= zabbix_script_dir %>/rabbitmq-status.sh
cd "$(dirname "$0")"

. .rab.auth

TYPE_OF_CHECK=$1
METRIC=$2
#rabbitmq[queues]
#rabbitmq[server,disk_free]

# This assumes that the server is going to then use zabbix_sender to feed the data BACK to the server.  Right now, I'm doing that
# in the python script

./api.py --username=$USERNAME --password=$PASSWORD --check=$TYPE_OF_CHECK --metric=$METRIC

