#!/bin/bash
#UserParameter=rabbitmq[*],<%= zabbix_script_dir %>/rabbitmq-status.sh

. /etc/zabbix/scripts/.rab.auth

VHOST=$1
METRIC=$2
QUEUE_NAME=$3

#rabbitmq[rabbit,vhost,queue_msg_unackd,queue-name]
if [ "$METRIC" = "queue_msg_unackd" ]; then
    /etc/zabbix/scripts/api.py --username=$USERNAME --password=$PASSWORD --vhost $VHOST check_queue $QUEUE_NAME messages_unacknowledged
fi

#rabbitmq[rabbit,vhost,queue_msgs,queue-name]
if [ "$METRIC" = "queue_msgs" ]; then
    /etc/zabbix/scripts/api.py --username=$USERNAME --password=$PASSWORD --vhost $VHOST check_queue $QUEUE_NAME messages
fi

#rabbitmq[rabbit,vhost,queue_memory,queue-name]
if [ "$METRIC" = "queue_memory" ]; then
    /etc/zabbix/scripts/api.py --username=$USERNAME --password=$PASSWORD --vhost $VHOST check_queue $QUEUE_NAME memory
fi

#rabbitmq[rabbit,vhost,queue_consumers,queue-name]
if [ "$METRIC" = "queue_consumers" ]; then
    /etc/zabbix/scripts/api.py --username=$USERNAME --password=$PASSWORD --vhost $VHOST check_queue $QUEUE_NAME consumers
fi

#rabbitmq[nodename,server,disk_free]
if [[ -z "$QUEUE_NAME" ]] && [[ "$VHOST" == "server" ]]; then
    /etc/zabbix/scripts/api.py --username=$USERNAME --password=$PASSWORD check_server $METRIC
fi
