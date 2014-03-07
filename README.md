rabbitmq-zabbix
=======================

Template and checks to monitor rabbitmq queues and server via Zabbix.

## WHY:
Because the SNMP plugin isn't an officially supported plugin, and rabbitmqctl based monitors are REALLY slow in comparison.

## WHAT:
Set of python scripts, zabbix template, and associated data to do autodiscovery

## HOW:
1. Install the files into /etc/zabbix/ folder, change permissions to Zabbix.
2. Create the .rab.auth file in scripts/ to use your monitoring username/password (defaulted to guest/guest).  Format should be username=guest and on a different line, password=guest
2a. Optionally add a filter. This allows you to restrict the queue list by any parameter in the queue details. It is a JSON-encoded string. Example: FILTER='{"durable": true}'
3. Import the template to your zabbix server
4. Make sure zabbix_sender is installed
6. **WARNING** Watch your process timeout.  I hit an issue with the amount of data and queues in rabbit where processing the results took longer than 3 seconds - that's the default timeout for the agent to kill a process.  If I can switch to a file based push instead of calling send for each item, this will hopefully reduce the time to send even further
7. Restart the local zabbix agent

Note courtesy of Lewis Franklin, you can set a filter on what is monitored to use only a specific set of queues.  Right now, you have to specify each of the queues you want monitored in a format like:
FILTER='{"name":"test_queue_two"}'
At some point I will probably make this more intelligent to allow regular expressions or more "ignore these queues" kind of things


## CHANGES
Updated to use zabbix_sender to push data on request to an item request.  This is similar to how the FromDual MySQL Zabbix stuff works and the concept was pulled from their templates.  

## Ideas for the future?
Add a local cache of the results (may be overkill for RabbitMQ).
Feel free to submit changes or ideas - mcintoshj@gmail.com


## Definite kudo's to some of the other developers around the web.  In particularly,
* Ptyhon Scripts: https://github.com/kmcminn/rabbit-nagios
* Base idea for the Rabbit template:  https://github.com/alfss/zabbix-rabbitmq
* Also need to thank Lewis Franklin https://github.com/brolewis for his contributions!
