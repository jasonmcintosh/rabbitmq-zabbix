rabbitmq-zabbix
=======================

Template and checks to monitor rabbitmq queues and server via Zabbix.

## WHY:
Because the SNMP plugin isn't an officially supported plugin, and rabbitmqctl based monitors are REALLY slow in comparison.

## WHAT:
Set of python scripts, zabbix template, and associated data to do autodiscovery

## HOW:
1. Install the files into /etc/zabbix/ folder, change permissions to Zabbix.
2. Update the .rab.auth file in scripts/ to use your monitoring username/password (defaulted to guest/guest)
2a. Optionally add a filter. This allows you to restrict the queue list by any parameter in the queue details. It is a JSON-encoded string. Example: FILTER='{"durable": true}'
3. Import the template to your zabbix server
4. Restart the local zabbix agent

## Definite kudo's to some of the other developers around the web.  In particularly,
* Ptyhon Scripts: https://github.com/kmcminn/rabbit-nagios
* Base idea for the Rabbit template:  https://github.com/alfss/zabbix-rabbitmq
