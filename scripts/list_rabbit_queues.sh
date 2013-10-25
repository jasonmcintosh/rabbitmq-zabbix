#!/bin/bash
. /etc/zabbix/scripts/rabbitmq/.rab.auth
printf "{"
printf "\"data\":"
/etc/zabbix/scripts/rabbitmq/list_rabbit_queues_json.py --username=$USERNAME --password=$PASSWORD -H `hostname -f`
printf "}"
