#!/bin/bash
#UserParameter=rabbitmq[*],<%= zabbix_script_dir %>/rabbitmq-status.sh

. /etc/zabbix/scripts/rabbitmq/.rab.auth

TYPE_OF_CHECK=$1
METRIC=$2

#rabbitmq[rabbit,vhost,queue_consumers,queue-name]
if [ "$TYPE_OF_CHECK" = "queues" ]; then
	/etc/zabbix/scripts/rabbitmq/check_rabbit_queue.py --username=$USERNAME --password=$PASSWORD -H `hostname -f` 
fi

#rabbitmq[nodename,server,disk_free]
if [[ "$TYPE_OF_CHECK" == "server" ]]; then
	/etc/zabbix/scripts/rabbitmq/check_rabbit_server.py --username=$USERNAME --password=$PASSWORD -H `hostname -f` --type=$2
fi

