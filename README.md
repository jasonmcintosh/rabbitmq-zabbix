rabbitmq-zabbix
=======================

Template and checks to monitor rabbitmq queues and server via Zabbix.

## WHY:
Because the SNMP plugin isn't an officially supported plugin, and rabbitmqctl based monitors are REALLY slow in comparison.

## WHAT:
Set of python scripts, zabbix template, and associated data to do autodiscovery

## HOW:
1. Install the files into /etc/zabbix/ folder, change permissions to Zabbix.
2. Setup configuration (see below)
3. Import the template to your zabbix server
4. Make sure zabbix_sender is installed
5. **WARNING** Watch your process timeout.  I hit an issue with the amount of data and queues in rabbit where processing the results took longer than 3 seconds - that's the default timeout for the agent to kill a process.  If I can switch to a file based push instead of calling send for each item, this will hopefully reduce the time to send even further
6. Restart the local zabbix agent


## CONFIGURATION:
You may optionally create a .rab.auth file in the scripts/ directory. This file allows you to change default parameters. The format is `VARIABLE=value`, one per line:
The default values are as follows:

    USERNAME=guest
    PASSWORD=guest
    CONF=/etc/zabbix/zabbix_agent.conf

You can also add a filter in this file to restrict which queues are monitored.
This item is a JSON-encoded string. The format provides some flexibility for
its use. You can either provide a single object or a list of objects to filter.
The available keys are: status, node, name, consumers, vhost, durable,
exclusive_consumer_tag, auto_delete, memory, policy

For example, the following filter could find all the durable queues:
`FILTER='{"durable": true}'`

To only use the durable queues for a given vhost, the filter would be:
`FILTER='{"durable": true, "vhost": "mine"}'`

To supply a list of queue names, the filter would be:
`FILTER='[{"name": "mytestqueuename"}, {"name": "queue2"}]'`

At some point the filters may be improved to include regular expressions or "ignore these queues"

## CHANGES
* Updated to use zabbix_sender to push data on request to an item request.  This is similar to how the FromDual MySQL Zabbix stuff works and the concept was pulled from their templates.
* Updated the filters to handle a list of objects


## Ideas for the future?
Add a local cache of the results (may be overkill for RabbitMQ).
Feel free to submit changes or ideas - mcintoshj@gmail.com


## Definite kudos to some of the other developers around the web.  In particular,
* Python Scripts: https://github.com/kmcminn/rabbit-nagios
* Base idea for the Rabbit template:  https://github.com/alfss/zabbix-rabbitmq
* Also need to thank Lewis Franklin https://github.com/brolewis for his contributions!
