#!/bin/bash
. /etc/zabbix/scripts/.rab.auth
/etc/zabbix/scripts/api.py --username=$USERNAME --password=$PASSWORD --check=list_queues --filter="$FILTER"
