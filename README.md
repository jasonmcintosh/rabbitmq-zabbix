rabbitmq-zabbix
=======================

<strong><note>Project is in ARCHIVED state.  I no longer work on zabbix nor rabbitmq, and don't have the time to maintain it.  If there are others who'd like to continue maintenance, feel free to reach out to me - ideally show it with a PR and an updated Readme ;)</strong>.  Note, for monitoring in general, I'd look at alternatives to Zabbix.  Most of what I see is SaaS or Prometheus and there are solutions for those platforms which are MUCH better supported at this point.  Sorry for the lack of updates but I have other projects I work on (Spinnaker is my main area of focus at this time, as well as DevOps automation for Cloud infrastructure)</note>

[![Build Status](https://travis-ci.org/jasonmcintosh/rabbitmq-zabbix.svg?branch=master)](https://travis-ci.org/jasonmcintosh/rabbitmq-zabbix)

Template and checks to monitor rabbitmq queues and server via Zabbix.

## SOURCE: 
https://github.com/jasonmcintosh/rabbitmq-zabbix

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
**Basic security recommendation** See https://www.rabbitmq.com/access-control.html for more information on access control.
```
When setting up a monitoring system, a general rule is that you should not to use tbe built-in
guest account.  Guest is an admin account with full permissions.  A basic suggestion is to setup 
a read only account who can access the management API.  Make sure that account is READ ONLY.  With 
one caveat - the monitoring user should be able execute the aliveness-test api.  That might mean
needing a slightly different set of permissions or pre-creation of the aliveness check queues.
IF using guest a warning - it can only access RabbitMQ management via localhost so you will 
need to set HOSTNAME=localhost

Below are sample commands to add a monitoring user with the required permissions.  Use these
at your own risk or as a starting point - NOT a finishing point!  

rabbitmqctl add_user zabbix pass
rabbitmqctl set_user_tags zabbix monitoring
rabbitmqctl set_permissions -p / zabbix '^aliveness-test$' '^amq\.default$' '^aliveness-test$'

```

You should create a `.rab.auth` file in the `scripts/rabbitmq` directory. This file allows you to change default parameters. The format is `VARIABLE=value`, one per line:
The default values are as follows:

    USERNAME=guest
    PASSWORD=guest
    CONF=/etc/zabbix/zabbix_agent.conf
    LOGLEVEL=INFO
    LOGFILE=/var/log/zabbix/rabbitmq_zabbix.log
    PORT=15672

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

To debug any potential issues, make sure the log directory exists and can be written to by zabbix, then set LOGLEVEL=DEBUG in the .rab.auth file and you'll get quite verbose output

### Macros

You can adjust the values for the critical and warning levels for the amount of messages by changing the following macros:

- RABBIT_QUEUE_MESSAGES_CRIT Defines the critical value for the amount of messages in a queue. It is set to 200000 messages per default
- RABBIT_QUEUE_MESSAGES_WARN Defines the warning value for the amount of messages in a queue. It is set to 100000 messages per default

## Low level discovery of queues, including GLOBAL REGULAR EXPRESSIONS:
`https://www.zabbix.com/documentation/3.0/manual/regular_expressions`
The low level discovery, which is what determines what queues to be monitored, requires with the existing template that a filter be defined as a global regular expression.  You can modify the template to do it in other ways, e.g. with a host level macro (NOT TESTED), or override it per host.  Or any number of methods.  But without a filter, NO queues will be discovered, JUST server level items will show up, and your checks will fail.

At some point the filters may be improved to include regular expressions or "ignore these queues"

## CHANGES
* Updated to use zabbix_sender to push data on request to an item request.  This is similar to how the FromDual MySQL Zabbix stuff works and the concept was pulled from their templates.
* Updated the filters to handle a list of objects


## Ideas for the future?
Add a local cache of the results (may be overkill for RabbitMQ).
Feel free to submit changes or ideas - mcintoshj@gmail.com

Repo:
https://github.com/jasonmcintosh/rabbitmq-zabbix

## Definite kudos to some of the other developers around the web.  In particular,
* Python Scripts: https://github.com/kmcminn/rabbit-nagios
* Base idea for the Rabbit template:  https://github.com/alfss/zabbix-rabbitmq
* Also need to thank Lewis Franklin https://github.com/brolewis for his contributions!
