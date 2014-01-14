#!/bin/bash
. /etc/zabbix/scripts/.rab.auth
/etc/zabbix/scripts/api.py --username=$USERNAME --password=$PASSWORD list_queues "$FILTER"
