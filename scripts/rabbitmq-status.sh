#!/bin/bash
#UserParameter=rabbitmq[*],<%= zabbix_script_dir %>/rabbitmq-status.sh

. /etc/zabbix/scripts/rabbitmq/.rab.auth

VHOST=$1
METRIC=$2
QUEUE_NAME=$3

#rabbitmq[rabbit,vhost,queue_msg_unackd,queue-name]
if [ "$METRIC" = "queue_msg_unackd" ]; then
	/etc/zabbix/scripts/rabbitmq/check_rabbit_queue.py --username=$USERNAME --password=$PASSWORD -H `hostname -f` --vhost $VHOST --queue=$QUEUE_NAME --item=messages_unacknowledged
fi

#rabbitmq[rabbit,vhost,queue_msgs,queue-name]
if [ "$METRIC" = "queue_msgs" ]; then
	/etc/zabbix/scripts/rabbitmq/check_rabbit_queue.py --username=$USERNAME --password=$PASSWORD -H `hostname -f` --vhost $VHOST --queue=$QUEUE_NAME --item=messages
fi

#rabbitmq[rabbit,vhost,queue_memory,queue-name]
if [ "$METRIC" = "queue_memory" ]; then
	/etc/zabbix/scripts/rabbitmq/check_rabbit_queue.py --username=$USERNAME --password=$PASSWORD -H `hostname -f` --vhost $VHOST --queue=$QUEUE_NAME --item=memory
fi

#rabbitmq[rabbit,vhost,queue_consumers,queue-name]
if [ "$METRIC" = "queue_consumers" ]; then
	/etc/zabbix/scripts/rabbitmq/check_rabbit_queue.py --username=$USERNAME --password=$PASSWORD -H `hostname -f` --vhost $VHOST --queue=$QUEUE_NAME --item=consumers
fi

#rabbitmq[nodename,server,disk_free]
if [[ -z "$QUEUE_NAME" ]] && [[ "$VHOST" == "server" ]]; then
	/etc/zabbix/scripts/rabbitmq/check_rabbit_server.py --username=$USERNAME --password=$PASSWORD -H `hostname -f` --type=$2
fi

